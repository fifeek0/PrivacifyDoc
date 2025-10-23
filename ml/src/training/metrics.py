"""
Metrics for NER evaluation.

Uses seqeval which computes metrics per-entity (not per-token).
"""

from typing import Dict, List
import numpy as np
from seqeval.metrics import (
    f1_score,
    precision_score,
    recall_score,
    classification_report
)

class NERMetrics:
    """Compute NER metrics (F1, Precision, Recall)."""

    def __init__(self,id2label: Dict[int,str]):
        """Initialize metric calculator.

        Args:
            id2label: Mapping from label ID to label name
        """
        self.id2label = id2label

    def compute_metrics(self, eval_pred) -> Dict[str, float]:
        """
                Compute metrics for evaluation.

                This function is called by HuggingFace Trainer.

                Args:
                    eval_pred: Tuple of (predictions, labels)
                        predictions: [batch_size, seq_len, num_labels]
                        labels: [batch_size, seq_len]

                Returns:
                    Dict with metrics: f1, precision, recall
                """

        predictions, labels = evval_pred
        predictions = np.argmax(predictions, axis=2)
        true_labels = []
        pred_labels = []

        for pred_seq, label_seq in zip(predictions, labels):
            true_seq = []
            pred_seq_labels = []

            for pred, label in zip(pred_seq, label_seq):
                if label != -100:
                    true_seq.append(self.id2label[label])
                    pred_seq_labels.append(self.id2label[pred])

            true_labels.append(true_seq)
            pred_labels.append(pred_seq_labels)

        return {
            'precision': precision_score(true_labels, pred_labels),
            'recall': recall_score(true_labels, pred_labels),
            'f1': f1_score(true_labels, pred_labels),
        }

    def detailed_report(
            self,
            predictions: np.ndarray,
            labels: np.ndarray,
    ):

        true_labels = []
        pred_labels = []
        for pred_seq, label_seq in zip(predictions, labels):
            true_seq = []
            pred_seq_labels = []

            for pred, label in zip(pred_seq, label_seq):
                if label != -100:
                    true_seq.append(self.id2label[label])
                    pred_seq_labels.append(self.id2label[pred])

            true_labels.append(true_seq)
            pred_labels.append(pred_seq_labels)

        return classification_report(true_labels, pred_labels)