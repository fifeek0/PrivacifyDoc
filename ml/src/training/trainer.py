"""
Main training logic using HuggingFace Trainer.
"""

import yaml
from pathlib import Path
from datetime import datetime
import torch
from transformers import (
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)

from .dataset import load_datasets
from .metrics import NERMetrics


class NERTrainer:
    """Trainer for NER model."""

    def __init__(self, config_path: str):
        """Initialize trainer.
        Args:
            config_path: Path to YAML config file
        """
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        model_config_path = Path(config_path).parent / "model_config.yaml"
        with open(model_config_path, "r") as f:
            self.model_config = yaml.safe_load(f)

        self.label2id = self.model_config['label2id']
        self.id2label = self.model_config['id2label']
        self._set_seed(self.config['seed'])
        self.experiment_dir = self._create_experiment_dir()
        print("=" * 60)
        print(f"EXPERIMENT: {self.config['experiment']['name']}")
        print("=" * 60)
        print(f"Output directory: {self.experiment_dir}")
        print(f"Model: {self.config['model']['name']}")
        print(f"Number of labels: {self.config['model']['num_labels']}")
        print()

    def _set_seed(self, seed: int):
        """Set random seed for reproducibility."""
        import random
        import numpy as np

        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def _create_experiment_dir(self) -> Path:
        """Create directory for this experiment."""
        base_dir = Path(self.config['training']['output_dir'])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_name = f"{self.config['experiment']['name']}_{timestamp}"

        exp_dir = base_dir / exp_name
        exp_dir.mkdir(parents=True, exist_ok=True)

        with open(exp_dir / "config.yaml", 'w') as f:
            yaml.dump(self.config, f)

        return exp_dir    
        
    def load_data(self):
        """Load training datasets."""
        print("Loading datasets...")

        data_config = self.config['data']

        self.train_dataset, self.val_dataset, self.test_dataset, self.tokenizer = load_datasets(
            train_path=data_config['train_path'],
            val_path=data_config['val_path'],
            test_path=data_config['test_path'],
            model_name=self.config['model']['name'],
            label2id=self.label2id,
            max_length=data_config['max_length']
        )

        print(f"  Train: {len(self.train_dataset)} examples")
        print(f"  Val:   {len(self.val_dataset)} examples")
        print(f"  Test:  {len(self.test_dataset)} examples")
        print()

    def load_model(self):
        """Load pre-trained model."""
        print("Loading model...")

        self.model = AutoModelForTokenClassification.from_pretrained(
            self.config['model']['name'],
            num_labels=self.config['model']['num_labels'],
            id2label=self.id2label,
            label2id=self.label2id,
            use_safetensors=True  # Force safetensors to avoid torch.load vulnerability
        )

        num_params = sum(p.numel() for p in self.model.parameters())
        num_trainable = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        print(f"  Total parameters: {num_params:,}")
        print(f"  Trainable parameters: {num_trainable:,}")
        print()

    def train(self):
        """Run training."""        
        print("Setting up training...")

        training_config = self.config['training']

        training_args = TrainingArguments(
            output_dir=str(self.experiment_dir / "checkpoints"),
            num_train_epochs=training_config['num_train_epochs'],
            per_device_train_batch_size=training_config['per_device_train_batch_size'],
            per_device_eval_batch_size=training_config['per_device_eval_batch_size'],
            learning_rate=training_config['learning_rate'],
            weight_decay=training_config['weight_decay'],
            warmup_steps=training_config['warmup_steps'],
            fp16=training_config.get('fp16', False),
            gradient_accumulation_steps=training_config.get('gradient_accumulation_steps', 1),
            eval_strategy=training_config['evaluation_strategy'],
            save_strategy=training_config['save_strategy'],
            load_best_model_at_end=training_config['load_best_model_at_end'],
            metric_for_best_model=training_config['metric_for_best_model'],
            logging_dir=str(self.experiment_dir / training_config['logging_dir']),
            logging_steps=training_config['logging_steps'],
            save_total_limit=3,  # Keep only 3 best checkpoints
            seed=self.config['seed']
        )

        metrics_calculator = NERMetrics(id2label=self.id2label)

        callbacks = []
        if 'early_stopping_patience' in training_config:
            callbacks.append(
                EarlyStoppingCallback(
                    early_stopping_patience=training_config['early_stopping_patience']
                )
            )

        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.val_dataset,
            tokenizer=self.tokenizer,
            compute_metrics=metrics_calculator.compute_metrics,
            callbacks=callbacks
        )

        print("Starting training...")
        print("=" * 60)

        self.trainer.train()

        print("=" * 60)
        print("✅ Training complete!")
        print()

    def evaluate(self):
        """Evaluate on test set."""
        print("Evaluating on test set...")

        test_results = self.trainer.evaluate(self.test_dataset)

        print("\nTest Results:")
        print(f"  F1 Score:  {test_results['eval_f1']:.4f}")
        print(f"  Precision: {test_results['eval_precision']:.4f}")
        print(f"  Recall:    {test_results['eval_recall']:.4f}")
        print()

        # Save test results
        import json
        with open(self.experiment_dir / "test_results.json", 'w') as f:
            json.dump(test_results, f, indent=2)

        return test_results

    def save_model(self):
        """Save final model."""
        model_dir = self.experiment_dir / "model"

        print(f"Saving model to {model_dir}...")

        self.trainer.save_model(str(model_dir))
        self.tokenizer.save_pretrained(str(model_dir))

        print("✓ Model saved")
        print()

    def run_full_pipeline(self):
        """Run complete training pipeline."""
        self.load_data()
        self.load_model()
        self.train()
        test_results = self.evaluate()
        self.save_model()

        print("=" * 60)
        print("🎉 TRAINING PIPELINE COMPLETE")
        print("=" * 60)
        print(f"\nExperiment directory: {self.experiment_dir}")
        print(f"Final Test F1: {test_results['eval_f1']:.4f}")
        print("\nNext steps:")
        print(f"  1. Review training logs: tensorboard --logdir {self.experiment_dir}/logs")
        print(f"  2. Test model: python scripts/evaluate.py --model-path {self.experiment_dir}/model")
