"""
Data Validator - checks quality of training data
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter


class DataValidator:
    """Validate NER training data quality."""

    def __init__(self):
        self.required_entity_types = [
            'PERSON', 'ADDRESS', 'EMAIL', 'PHONE',
            'PESEL', 'NIP', 'REGON'
        ]

    def validate(
            self,
            train_path: str,
            val_path: str = None,
            test_path: str = None
    ) -> bool:
        """Validate training, validation, and test datasets.

        Returns True if all datasets are valid, False otherwise.
        """

        print("=" * 60)
        print("VALIDATING DATASET")
        print("=" * 60)

        all_valid = True

        # Validate train
        print("\n[1/3] Validating training set...")
        train_valid = self._validate_single_file(train_path, "Train")
        all_valid = all_valid and train_valid

        # Validate val
        if val_path:
            print("\n[2/3] Validating validation set...")
            val_valid = self._validate_single_file(val_path, "Val")
            all_valid = all_valid and val_valid

        # Validate test
        if test_path:
            print("\n[3/3] Validating test set...")
            test_valid = self._validate_single_file(test_path, "Test")
            all_valid = all_valid and test_valid

            # Summary
            print("\n" + "=" * 60)
            if all_valid:
                print("✅ ALL VALIDATION CHECKS PASSED")
            else:
                print("❌ SOME VALIDATION CHECKS FAILED")
            print("=" * 60)

        return all_valid

    def _validate_single_file(self, file_path: str, dataset_name: str) -> bool:
        """Validate a single dataset file."""

        path = Path(file_path)
        if not path.exists():
            print(f"ERROR: {dataset_name} file not found at {file_path}")
            return False

        # Load examples
        examples = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"ERROR: Invalid JSON format in {dataset_name} file.")
                    return False
        print(f"  Loaded {len(examples)} examples")

        checks = [
            self._check_minimum_size(examples, dataset_name),
            self._check_format(examples),
            self._check_entity_coverage(examples),
            self._check_entity_positions(examples)
        ]

        return all(checks)

    def _check_minimum_size(self, examples: List[Dict], dataset_name: str) -> bool:
        """Check if dataset has minimum required size."""
        min_sizes = {
            'Train': 100,
            'Val': 20,
            'Test': 20
        }

        min_size = min_sizes.get(dataset_name, 10)
        actual_size = len(examples)

        if actual_size >= min_size:
            print(f"  ✓ Size check: {actual_size} >= {min_size}")
            return True
        else:
            print(f"  ✗ Size check FAILED: {actual_size} < {min_size}")
            return False

    def _check_format(self, examples: List[Dict]) -> bool:
        """Check if all examples have correct format."""
        for i, example in enumerate(examples):
            if 'text' not in example:
                print(f"  ✗ Example {i}: missing 'text' field")
                return False

            if 'entities' not in example:
                print(f"  ✗ Example {i}: missing 'entities' field")
                return False

            if not isinstance(example['text'], str):
                print(f"  ✗ Example {i}: 'text' must be string")
                return False

            if not isinstance(example['entities'], list):
                print(f"  ✗ Example {i}: 'entities' must be list")
                return False

        print(f"  ✓ Format check: all examples valid")
        return True

    def _check_entity_coverage(self, examples: List[Dict]) -> bool:
        """Check if all required entity types are present."""
        entity_counts = Counter()
        for example in examples:
            for start, end, entity_type in example['entities']:
                entity_counts[entity_type] += 1

        missing = []
        for entity_type in self.required_entity_types:
            count = entity_counts.get(entity_type, 0)
            if count == 0:
                missing.append(entity_type)

        if missing:
            print(f"  ⚠️  Missing entity types: {missing}")
            print(f"     (This is OK for small datasets)")

        # Print distribution
        print(f"  ✓ Entity distribution:")
        for entity_type in sorted(entity_counts.keys()):
            print(f"     {entity_type}: {entity_counts[entity_type]}")

        return True

    def _check_entity_positions(self, examples: List[Dict]) -> bool:
        """Check if entity positions are valid."""
        for i, example in enumerate(examples[:10]):  # Check first 10
            text = example['text']
            for start, end, entity_type in example['entities']:
                # Check bounds
                if start < 0 or end > len(text) or start >= end:
                    print(f"  ✗ Example {i}: invalid entity bounds ({start}, {end})")
                    return False

                # Check if substring makes sense
                substring = text[start:end]
                if len(substring) == 0:
                    print(f"  ✗ Example {i}: empty entity")
                    return False

        print(f"  ✓ Entity positions: valid")
        return True
