#!/usr/bin/env python3
"""
Train NER model.

Usage:
    python scripts/train.py --config config/training_config.yaml
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from training.trainer import NERTrainer


def main():
    parser = argparse.ArgumentParser(description="Train NER model")

    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to training config YAML"
    )

    args = parser.parse_args()

    # Validate config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)

    # Create trainer
    trainer = NERTrainer(config_path=str(config_path))

    # Run training pipeline
    try:
        trainer.run_full_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Training failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()