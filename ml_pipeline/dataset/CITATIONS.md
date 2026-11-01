# Dataset Citations & Provenance Documentation

## Overview
This document records the provenance, licensing, category mapping rationale, and distribution of the curated waste classification dataset used in the Smart Waste Management System (SWMS) machine learning pipeline.

---

## 1. Source Dataset Attribution

- **Dataset Name**: Garbage Classification (12 classes)
- **Original Author**: Mostafa Abla
- **Original Publication**: Mendeley Data, V1, 2020 (doi: [10.17632/m4nzt5hxns.1](https://doi.org/10.17632/m4nzt5hxns.1))
- **Public Mirror / Repository**: Hugging Face Datasets (`UdaraChamidu/Garbage-Classification-with-12-classes`)
- **Repository URL**: [https://huggingface.co/datasets/UdaraChamidu/Garbage-Classification-with-12-classes](https://huggingface.co/datasets/UdaraChamidu/Garbage-Classification-with-12-classes)
- **Direct Archive URL**: [https://huggingface.co/datasets/UdaraChamidu/Garbage-Classification-with-12-classes/resolve/main/garbage_classification.zip](https://huggingface.co/datasets/UdaraChamidu/Garbage-Classification-with-12-classes/resolve/main/garbage_classification.zip)
- **License**: Creative Commons Attribution 4.0 International ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))

### Academic Citation
```bibtex
@article{abla2020garbage,
  title={Garbage Classification (12 classes)},
  author={Abla, Mostafa},
  journal={Mendeley Data},
  volume={1},
  year={2020},
  doi={10.17632/m4nzt5hxns.1}
}
```

---

## 2. Category Mapping Rationale

The original 12-class dataset contains twelve waste types. For the SWMS Day 1 scope, three target classes are extracted and standardized into municipal waste management streams:

| Source Class (Abla) | Target Class (SWMS) | Description & Material Scope | Waste Stream Classification |
|---|---|---|---|
| `biological` | `organic` | Food waste, fruit peels, vegetable scraps, and decomposed matter | Compostable / Organic Waste |
| `plastic` | `plastic` | Plastic bottles, containers, bags, cups, and polymers | Recyclable / Inorganic Plastic |
| `paper` | `paper` | Clean paper, cardboard-paper sheets, office documents, newspapers | Recyclable / Inorganic Paper |

### Mapping Details
- **`biological` -> `organic`**: In municipal waste sorting systems, biodegradable food scraps and garden materials constitute the primary organic waste stream. Abla's `biological` class depicts fruits, vegetables, food scraps, and organic matter, making it a 1:1 match for the `organic` classification requirement.
- **`plastic` -> `plastic`**: Direct mapping. Includes HDPE, PET, and other post-consumer plastic containers and packaging.
- **`paper` -> `paper`**: Direct mapping. Includes paper sheets, printed materials, and standard non-waxed paper waste.

---

## 3. Dataset Distribution & Partitioning

The curated dataset consists of **210 real-world photographic images**, sampled deterministically with random seed `42` for exact reproducibility.

- **Split Ratio**: 80% Training / 20% Validation
- **Images per Class**: 70 images (56 Train, 14 Val)
- **Total Dataset Size**: 210 images (168 Train, 42 Val)

### Distribution Table

| Category | Train Count (80%) | Validation Count (20%) | Total Count | Format / Mode | Min Resolution |
|---|---|---|---|---|---|
| **Organic Waste** (`organic`) | 56 | 14 | 70 | JPEG (RGB) | 183 x 129 |
| **Plastic Waste** (`plastic`) | 56 | 14 | 70 | JPEG (RGB) | 183 x 168 |
| **Paper Waste** (`paper`) | 56 | 14 | 70 | JPEG (RGB) | 183 x 140 |
| **Total** | **168** | **42** | **210** | **RGB** | — |

---

## 4. Quality & Integrity Assurance

Every curated image has been programmatically inspected and verified using the Pillow (`PIL.Image`) library:
1. **Format & Integrity**: Verified with `PIL.Image.open().verify()`. No truncated, zero-byte, or corrupted files.
2. **Color Space**: Confirmed 3-channel standard RGB mode (`mode == 'RGB'`).
3. **Dimensions**: All images meet or exceed standard deep learning transfer learning input requirements (MobileNetV2 224x224).
4. **Authenticity**: Real photographs of waste items captured under natural lighting conditions on varied indoor and outdoor backgrounds.
