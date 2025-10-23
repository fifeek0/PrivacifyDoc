#!/usr/bin/env python3
"""
Generate synthetic training data for NER.

Usage:
    python scripts/generate_data.py --num-examples 3000 --output data/processed/
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from data_generation.synthetic_generator import SyntheticDataGenerator, split_dataset


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic NER training data")

    parser.add_argument(
        "--num-examples",
        type=int,
        default=3000,
        help="Total number of examples to generate (default: 3000)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/",
        help="Output directory (default: data/processed/)"
    )

    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Training set ratio (default: 0.8)"
    )

    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.1,
        help="Validation set ratio (default: 0.1)"
    )

    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.1,
        help="Test set ratio (default: 0.1)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )

    args = parser.parse_args()

    # Validate ratios
    if abs(args.train_ratio + args.val_ratio + args.test_ratio - 1.0) > 1e-6:
        print("ERROR: Ratios must sum to 1.0")
        sys.exit(1)

        # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("GENERATING SYNTHETIC NER TRAINING DATA")
    print("=" * 60)
    print(f"Total examples: {args.num_examples}")
    print(f"Train/Val/Test split: {args.train_ratio}/{args.val_ratio}/{args.test_ratio}")
    print(f"Output directory: {output_dir}")
    print(f"Random seed: {args.seed}")
    print()

    # Generate data
    generator = SyntheticDataGenerator(seed=args.seed)

    print("Generating examples...")
    examples = generator.generate_batch(
        num_examples=args.num_examples,
        show_progress=True
    )

    print(f"\n✓ Generated {len(examples)} examples")

    # Split
    print("\nSplitting dataset...")
    train, val, test = split_dataset(
        examples,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )

    print(f"  Train: {len(train)} examples")
    print(f"  Val:   {len(val)} examples")
    print(f"  Test:  {len(test)} examples")

    # Save
    print("\nSaving datasets...")
    generator.save_dataset(train, output_dir / "train.jsonl")
    generator.save_dataset(val, output_dir / "val.jsonl")
    generator.save_dataset(test, output_dir / "test.jsonl")

    print("\n" + "=" * 60)
    print("✅ DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nDatasets saved to: {output_dir}")
    print("\nNext steps:")
    print("  1. Inspect data: head data/processed/train.jsonl")
    print("  2. Train model: python scripts/train.py")


if __name__ == "__main__":
    main()