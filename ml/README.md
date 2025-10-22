# PrivacifyDoc ML Training Service

Fine-tuning service dla Named Entity Recognition na polskich danych wrażliwych.

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Generate training data
python scripts/generate_data.py --num-examples 3000

# Train model
python scripts/train.py --config config/training_config.yaml

# Evaluate
python scripts/evaluate.py --model-path experiments/exp_001/model/
```

## Structure
- `data/` - Training datasets
- `src/` - Source code
- `experiments/` - Training runs
- `models/` - Production models
- `notebooks/` - Analysis notebooks