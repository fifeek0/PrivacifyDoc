"""
Dataset loader for NER training.

Handles:
- Loading JSONL data
- Tokenization
- Label alignment with tokens
"""

import json
from typing import Dict, List
from pathlib import Path
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer

class NERDataset(Dataset):
    """PyTorch Dataset for NER."""

    def __init__(
            self,
            data_path: str,
            tokenizer: AutoTokenizer,
            label2id: Dict[str, int],
            max_length: int = 128
    ):
        """
                Initialize dataset.

                Args:
                    data_path: Path to JSONL file
                    tokenizer: HuggingFace tokenizer
                    label2id: Mapping from label name to ID
                    max_length: Maximum sequence length
                """
        self.tokenizer = tokenizer
        self.label2id = label2id
        self.max_length = max_length
        self.examples = self._load_data(data_path)

    def _load_data(self, data_path: str) -> List[Dict]:
        """Load examples from JSONL."""
        examples = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                examples.append(json.loads(line))
        return examples

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get single example.

        Returns:
            Dict with:
                - input_ids: [seq_len]
                - attention_mask: [seq_len]
                - labels: [seq_len]
        """
        example = self.examples[idx]

        # Tokenize
        encoding = self.tokenizer(
            example['text'],
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_offsets_mapping=True # To align labels
        )

        labels = self._align_labels_with_tokens(
            example['text'],
            example['entities'],
            encoding['offset_mapping']
        )

        return {
            'input_ids': torch.tensor(encoding['input_ids']),
            'attention_mask': torch.tensor(encoding['attention_mask']),
            'labels': torch.tensor(labels)
        }

    def _align_labels_with_tokens(
            self,
            text: str,
            entities: List[tuple],
            offset_mapping: List[tuple]
    ) -> List[int]:
        """
             Align entity labels with tokenized text.

             This is the CRITICAL part for NER!

             Args:
                 text: Original text
                 entities: List of (start, end, label) tuples
                 offset_mapping: Token offsets from tokenizer

             Returns:
                 List of label IDs aligned with tokens
             """

        labels = [self.label2id['O']] * len(offset_mapping)

        # Build entity spans for fast lookup
        entity_spans = []  # (start, end, label)
        for start, end, entity_type in entities:
            entity_spans.append((start, end, entity_type))

        for token_idx, (start, end) in enumerate(offset_mapping):
            if start == 0 and end == 0:
                labels[token_idx] = -100
                continue

            assigned = False
            for ent_start, ent_end, ent_type in entity_spans:
                # Token and entity overlap if they share any character
                if start < ent_end and end > ent_start:
                    if start == ent_start:
                        labels[token_idx] = self.label2id[f'B-{ent_type}']
                    else:
                        labels[token_idx] = self.label2id[f'I-{ent_type}']
                    assigned = True
                    break
            if not assigned:
                labels[token_idx] = self.label2id['O']

        return labels


def load_datasets(
        train_path: str,
        val_path: str,
        test_path: str,
        model_name: str,
        label2id: Dict[str, int],
        max_length: int = 128
) -> tuple:
    """
    Load train/val/test datasets.

    Args:
        train_path: Path to training data
        val_path: Path to validation data
        test_path: Path to test data
        model_name: HuggingFace model name (for tokenizer)
        label2id: Label to ID mapping
        max_length: Max sequence length

    Returns:
        (train_dataset, val_dataset, test_dataset)
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    train_dataset = NERDataset(train_path, tokenizer, label2id, max_length)
    val_dataset = NERDataset(val_path, tokenizer, label2id, max_length)
    test_dataset = NERDataset(test_path, tokenizer, label2id, max_length)

    return train_dataset, val_dataset, test_dataset, tokenizer