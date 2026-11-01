# E2E Test Infra: Smart Waste Management System (SWMS) - Day 1

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation internal details.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.
- Executable via standalone Python runner `tests/e2e_runner.py` with exit code 0 on pass.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|---------------------|:------:|:------:|:------:|:------:|
| F1| Monorepo Structure | ORIGINAL_REQUEST §R1, TASKS.md 1.1 | 5 | 5 | ✓ | ✓ |
| F2| Dataset Curation & Partition | ORIGINAL_REQUEST §R2, TASKS.md 1.2 | 5 | 5 | ✓ | ✓ |
| F3| Dataset Citations & Provenance | ORIGINAL_REQUEST §R2, SPEC.md | 5 | 5 | ✓ | ✓ |
| F4| ML Training Pipeline | ORIGINAL_REQUEST §R3, TASKS.md 1.3 | 5 | 5 | ✓ | ✓ |
| F5| Model Export (`waste_model.pth`) | ORIGINAL_REQUEST §R4, TASKS.md 1.5 | 5 | 5 | ✓ | ✓ |
| F6| Evaluation Visualizations & Metrics | ORIGINAL_REQUEST §R4, TASKS.md 1.4 | 5 | 5 | ✓ | ✓ |
| F7| Model Inference & Contract | ADR.md, API_SPECS.md | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test Runner: `tests/e2e_runner.py` (standard Python, outputs TAP or clean test summary table, exit code 0 on all pass)
- Test Directory: `tests/`
- Verification semantics:
  - Tier 1: Directory presence, file existence, image counts per class, model file valid PyTorch checkpoint, image dimensions.
  - Tier 2: Boundary counts (>=50/class, 80/20 train/val ratio within tolerance, accuracy >= 80%, precision/recall/F1 >= 0.75, image file integrity, non-zero file sizes).
  - Tier 3: Model loadability with torchvision MobileNetV2 architecture, inference output keys match API specification contract (`category`, `confidence`, `probabilities`).
  - Tier 4: End-to-end synthetic image inference simulation, classification report parsing, confusion matrix dimension check (3x3).

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full Model Load & Classify Single Waste Image | F4, F5, F7 | Medium |
| 2 | Model Robustness Across Different Valid Aspect Ratios | F5, F7 | Medium |
| 3 | Classification Report Metric Integrity Verification | F6 | Low |
| 4 | Monorepo Stubs Importability & Syntax Validation | F1 | Low |
| 5 | Dataset Balance & Split Ratio Verification | F2, F3 | Low |

## Coverage Thresholds
- Tier 1: ≥5 per feature (total ≥35 tests)
- Tier 2: ≥5 per feature (total ≥35 tests)
- Tier 3: ≥7 pairwise tests
- Tier 4: ≥5 realistic application scenarios
- Total: ≥82 tests
