#!/usr/bin/env python3
"""
Evaluate trained NER model.

Usage:
    python scripts/evaluate.py --model-path experiments/exp_001/model/
"""

import argparse
import sys
from pathlib import Path
import yaml
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from training.dataset import NERDataset
from training.metrics import NERMetrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate NER model")

    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="Path to trained model directory"
    )

    parser.add_argument(
        "--test-data",
        type=str,
        default="data/processed/test.jsonl",
        help="Path to test data (default: data/processed/test.jsonl)"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size for evaluation (default: 16)"
    )

    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        print(f"ERROR: Model not found: {model_path}")
        sys.exit(1)

    print("=" * 60)
    print("EVALUATING NER MODEL")
    print("=" * 60)
    print(f"Model: {model_path}")
    print(f"Test data: {args.test_data}")
    print()

    model_config_path = Path("config/model_config.yaml")
    with open(model_config_path, 'r') as f:
        model_config = yaml.safe_load(f)

    label2id = model_config['label2id']
    id2label = model_config['id2label']

    print("Loading model...")
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    print(f"  Device: {device}")
    print()

    print("Loading test dataset...")
    test_dataset = NERDataset(
        data_path=args.test_data,
        tokenizer=tokenizer,
        label2id=label2id,
        max_length=128
    )
    print(f"  Test examples: {len(test_dataset)}")
    print()

    from torch.utils.data import DataLoader
    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False
    )

    print("Evaluating...")
    all_predictions = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels']

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = outputs.logits.cpu().numpy()

            all_predictions.append(predictions)
            all_labels.append(labels.numpy())

    import numpy as np
    all_predictions = np.concatenate(all_predictions, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    metrics_calculator = NERMetrics(id2label=id2label)

    metrics = metrics_calculator.compute_metrics((all_predictions, all_labels))

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print()

    print("Detailed Classification Report:")
    print("=" * 60)
    report = metrics_calculator.detailed_report(all_predictions, all_labels)
    print(report)

    # Save results
    output_file = model_path.parent / "evaluation_results.json"
    import json
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()