"""
PyTorch MobileNetV2 Transfer Learning Training Pipeline for Waste Classification.
Smart Waste Management System (SWMS) - Bilcode Technology Take-Home Assessment.

Features:
- MobileNetV2 architecture with ImageNet pretrained weights.
- Custom 3-class classifier head with Dropout and Linear layer.
- Comprehensive data augmentation for training (random crop, flip, rotation, jitter).
- Standard ImageNet normalization for validation.
- Reproducibility via random seed control.
- Two-phase training: warm-up classifier head followed by fine-tuning top feature blocks.
- Checkpoint export: saves waste_model.pth and class_to_idx.json.
- Convenience exports to project root.
- Generates loss/accuracy curves.
"""

import argparse
import copy
import json
import os
from pathlib import Path
import random
import shutil
import time

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import MobileNet_V2_Weights, mobilenet_v2


def set_seed(seed: int = 42) -> None:
    """Set random seed for reproducibility across torch, numpy, and random."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    """Select compute device with CPU fallback."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    return device


def get_data_transforms():
    """Build data augmentation transforms for training and standard normalization for validation."""
    data_transforms = {
        "train": transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ]),
        "val": transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    }
    return data_transforms


def create_model(num_classes: int = 3, pretrained: bool = True) -> nn.Module:
    """Instantiate MobileNetV2 with custom 3-class classifier head."""
    if pretrained:
        weights = MobileNet_V2_Weights.DEFAULT
        model = mobilenet_v2(weights=weights)
    else:
        model = mobilenet_v2(weights=None)

    # Freeze base feature extractor initially
    for param in model.features.parameters():
        param.requires_grad = False

    # Replace classifier: Dropout(p=0.2) + Linear(1280, num_classes)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(model.last_channel, num_classes)
    )
    return model


def train_model(
    model: nn.Module,
    dataloaders: dict,
    dataset_sizes: dict,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    scheduler,
    device: torch.device,
    epochs: int = 15,
    fine_tune_epoch: int = 4
) -> tuple:
    """
    Execute training loop with validation tracking and best-checkpoint selection.
    
    Fine-tuning strategy:
    - Epochs 1 to fine_tune_epoch: only classifier head is updated (fast convergence).
    - Epochs fine_tune_epoch+ to end: unfreeze top feature blocks (features[14:]) with lower lr.
    """
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    history = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": []
    }

    for epoch in range(1, epochs + 1):
        print(f"\n--- Epoch {epoch}/{epochs} ---")

        # Fine-tune transition
        if epoch == fine_tune_epoch:
            print("[Info] Unfreezing top feature layers for domain fine-tuning...")
            for param in model.features[14:].parameters():
                param.requires_grad = True
            # Recreate optimizer with differential learning rates
            optimizer = optim.Adam([
                {"params": model.features[14:].parameters(), "lr": 1e-4},
                {"params": model.classifier.parameters(), "lr": 5e-4}
            ], weight_decay=1e-4)

        for phase in ["train", "val"]:
            if phase == "train":
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            if phase == "train" and scheduler is not None:
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double().item() / dataset_sizes[phase]

            if phase == "train":
                history["train_loss"].append(epoch_loss)
                history["train_acc"].append(epoch_acc)
            else:
                history["val_loss"].append(epoch_loss)
                history["val_acc"].append(epoch_acc)

            print(f"{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f} ({epoch_acc * 100:.2f}%)")

            # Checkpoint best validation model
            if phase == "val" and epoch_acc >= best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

    time_elapsed = time.time() - since
    print(f"\nTraining completed in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s")
    print(f"Best Validation Accuracy: {best_acc:.4f} ({best_acc * 100:.2f}%)")

    model.load_state_dict(best_model_wts)
    return model, history, best_acc


def plot_accuracy_curve(history: dict, output_path: Path, root_path: Path = None) -> None:
    """Plot and save training and validation loss and accuracy curves."""
    epochs = range(1, len(history["train_loss"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=150)

    # Loss subplot
    ax1.plot(epochs, history["train_loss"], "b-o", label="Training Loss")
    ax1.plot(epochs, history["val_loss"], "r--s", label="Validation Loss")
    ax1.set_title("Training & Validation Loss", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Epoch", fontsize=11)
    ax1.set_ylabel("Cross Entropy Loss", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right", frameon=True)

    # Accuracy subplot
    ax2.plot(epochs, [a * 100 for a in history["train_acc"]], "b-o", label="Training Accuracy")
    ax2.plot(epochs, [a * 100 for a in history["val_acc"]], "g--s", label="Validation Accuracy")
    ax2.axhline(y=80.0, color="crimson", linestyle=":", label="Requirement (>=80%)")
    ax2.axhline(y=85.0, color="darkorange", linestyle="--", label="Target (>=85%)")
    ax2.set_title("Training & Validation Accuracy", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Epoch", fontsize=11)
    ax2.set_ylabel("Accuracy (%)", fontsize=11)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="lower right", frameon=True)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"[Saved] Accuracy curve saved to {output_path}")

    if root_path is not None:
        try:
            shutil.copy2(output_path, root_path)
            print(f"[Export] Copied accuracy curve to root: {root_path}")
        except Exception as e:
            print(f"[Warning] Failed to copy accuracy curve to root: {e}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Train MobileNetV2 for Waste Classification")
    parser.add_argument("--data-dir", type=str, default=None, help="Path to dataset directory containing train/ and val/")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=1e-3, help="Initial learning rate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--save-dir", type=str, default=None, help="Directory to save model weights")
    args = parser.parse_args()

    # Determine project and dataset directories
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    if args.data_dir is not None:
        data_dir = Path(args.data_dir).resolve()
    else:
        # Check standard locations
        candidates = [
            script_dir / "dataset",
            project_root / "ml_pipeline" / "dataset",
            Path("ml_pipeline/dataset").resolve(),
            Path("dataset").resolve()
        ]
        data_dir = None
        for cand in candidates:
            if (cand / "train").is_dir() and (cand / "val").is_dir():
                data_dir = cand
                break
        if data_dir is None:
            raise FileNotFoundError(f"Could not locate dataset directory in {candidates}")

    save_dir = Path(args.save_dir).resolve() if args.save_dir else (script_dir / "saved_models")
    artifacts_dir = script_dir / "artifacts"
    save_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    set_seed(args.seed)
    device = get_device()
    print(f"===========================================================")
    print(f" Smart Waste Management System (SWMS) - ML Training")
    print(f" Architecture: MobileNetV2 Transfer Learning")
    print(f" Compute Device: {device}")
    print(f" Dataset Path: {data_dir}")
    print(f" Epochs: {args.epochs} | Batch Size: {args.batch_size} | LR: {args.lr}")
    print(f"===========================================================")

    data_transforms = get_data_transforms()
    image_datasets = {
        x: datasets.ImageFolder(data_dir / x, data_transforms[x])
        for x in ["train", "val"]
    }
    dataloaders = {
        x: DataLoader(image_datasets[x], batch_size=args.batch_size, shuffle=(x == "train"), num_workers=0)
        for x in ["train", "val"]
    }
    dataset_sizes = {x: len(image_datasets[x]) for x in ["train", "val"]}
    class_names = image_datasets["train"].classes
    print(f"Classes discovered: {class_names}")
    print(f"Dataset split: Train={dataset_sizes['train']} images, Val={dataset_sizes['val']} images")

    # Formal class mapping
    slug_to_formal = {
        "organic": "Organic Waste",
        "paper": "Paper Waste",
        "plastic": "Plastic Waste"
    }
    formal_class_to_idx = {
        slug_to_formal.get(name, name): idx
        for idx, name in enumerate(class_names)
    }

    # Save class_to_idx.json
    class_to_idx_path = save_dir / "class_to_idx.json"
    with open(class_to_idx_path, "w", encoding="utf-8") as f:
        json.dump(formal_class_to_idx, f, indent=2)
    print(f"[Saved] Class mapping saved to {class_to_idx_path}: {formal_class_to_idx}")

    # Build model
    model = create_model(num_classes=len(class_names), pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # Train model
    model, history, best_acc = train_model(
        model=model,
        dataloaders=dataloaders,
        dataset_sizes=dataset_sizes,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        device=device,
        epochs=args.epochs,
        fine_tune_epoch=4
    )

    # Save model checkpoint
    model_save_path = save_dir / "waste_model.pth"
    torch.save(model.state_dict(), model_save_path)
    print(f"[Saved] Trained model weights saved to {model_save_path}")

    # Copy to project root
    root_model_path = project_root / "waste_model.pth"
    try:
        shutil.copy2(model_save_path, root_model_path)
        print(f"[Export] Copied model checkpoint to root: {root_model_path}")
    except Exception as e:
        print(f"[Warning] Failed to copy model checkpoint to root: {e}")

    # Save training history JSON
    history_path = artifacts_dir / "training_history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    print(f"[Saved] Training history saved to {history_path}")

    # Generate accuracy curve
    curve_output_path = artifacts_dir / "accuracy_curve.png"
    root_curve_path = project_root / "accuracy_curve.png"
    plot_accuracy_curve(history, curve_output_path, root_curve_path)

    print("\n[Done] Training pipeline completed successfully.")
    print(f"Final Validation Accuracy: {best_acc * 100:.2f}% (Threshold >= 80%, Target >= 85%)")


if __name__ == "__main__":
    main()
