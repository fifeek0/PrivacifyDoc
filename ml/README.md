# PrivacifyDoc ML Training Service

Fine-tuning service dla Named Entity Recognition (NER) na polskich danych wrażliwych.

## 📋 Spis treści

- [Architektura](#architektura)
- [Quick Start](#quick-start)
- [Szczegółowy przewodnik](#szczegółowy-przewodnik)
- [Konfiguracja](#konfiguracja)
- [Troubleshooting](#troubleshooting)
- [Performance Benchmarks](#performance-benchmarks)

---

## 🏗️ Architektura
```
┌─────────────────────────────────────────────────────────┐
│                   ML Training Pipeline                   │
└─────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Data Gen   │ ───> │   Training   │ ───> │  Evaluation  │
│  (Synthetic) │      │  (HerBERT)   │      │  (Test Set)  │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                      │
       v                     v                      v
   train.jsonl          checkpoints/           test_results.json
   val.jsonl            model/                 
   test.jsonl           logs/                  
```

**Komponenty:**

1. **Data Generation** - Generowanie syntetycznych danych treningowych
   - Template-based generation
   - Faker dla realistycznych danych PL
   - Valid checksums (PESEL, NIP)

2. **Training** - Fine-tuning HerBERT dla NER
   - Base model: `allegro/herbert-base-cased`
   - 10 klas: O, B-PERSON, I-PERSON, B-ADDRESS, I-ADDRESS, B-EMAIL, B-PHONE, B-PESEL, B-NIP, B-REGON
   - Mixed precision (FP16) dla szybszego treningu

3. **Evaluation** - Ocena modelu
   - Metrics: F1, Precision, Recall (per-entity, nie per-token)
   - Detailed classification report
   - Test set evaluation

---

## 🚀 Quick Start

### Wymagania

- Python 3.10+
- CUDA-capable GPU (rekomendowane, ale nie wymagane)
- 8GB+ RAM
- 10GB+ wolnego miejsca na dysku

### Instalacja
```bash
# 1. Przejdź do folderu ML
cd ml/

# 2. Stwórz virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Zainstaluj dependencies
pip install -r requirements.txt
```

### Szybki start (5 minut)
```bash
# Krok 1: Wygeneruj dane treningowe (3000 przykładów)
python scripts/generate_data.py --num-examples 3000

# Krok 2: Trenuj model (~30-60 min na GPU, ~2-3h na CPU)
python scripts/train.py --config config/training_config.yaml

# Krok 3: Ewaluuj model
# (Znajdź ścieżkę do modelu w outputs)
python scripts/evaluate.py --model-path experiments/herbert-ner-baseline_YYYYMMDD_HHMMSS/model/
```

**Oczekiwane rezultaty:**
- Test F1 Score: **0.85 - 0.92** (w zależności od datasetu)
- Training time: **30-60 minut** na RTX 4080
- Model size: **~450 MB**

---

## 📚 Szczegółowy przewodnik

### 1. Generowanie danych

**Podstawowe użycie:**
```bash
python scripts/generate_data.py \
    --num-examples 3000 \
    --output data/processed/ \
    --seed 42
```

**Zaawansowane opcje:**
```bash
python scripts/generate_data.py \
    --num-examples 5000 \
    --output data/custom/ \
    --train-ratio 0.7 \
    --val-ratio 0.15 \
    --test-ratio 0.15 \
    --seed 123
```

**Walidacja danych:**
```python
from src.data_generation.data_validator import DataValidator

validator = DataValidator()
is_valid = validator.validate(
    train_path="data/processed/train.jsonl",
    val_path="data/processed/val.jsonl",
    test_path="data/processed/test.jsonl"
)
```

### 2. Trening modelu

**Podstawowa konfiguracja:**

Edytuj `config/training_config.yaml` jeśli potrzebujesz zmienić hyperparametry:
```yaml
training:
  num_train_epochs: 5          # Liczba epok
  per_device_train_batch_size: 16  # Batch size (zmniejsz jeśli OOM)
  learning_rate: 2.0e-5        # Learning rate
  warmup_steps: 500            # Warmup steps
  early_stopping_patience: 3   # Early stopping
```

**Uruchomienie treningu:**
```bash
python scripts/train.py --config config/training_config.yaml
```

**Monitoring treningu:**
```bash
# TensorBoard (w osobnym terminalu)
tensorboard --logdir experiments/

# Otwórz w przeglądarce: http://localhost:6006
```

**Co oglądać w TensorBoard:**
- **Loss curves** - train loss powinien spadać, val loss nie powinien rosnąć
- **Metrics** - F1/Precision/Recall powinny rosnąć
- **Learning rate schedule** - sprawdź warmup i decay

### 3. Ewaluacja

**Test set evaluation:**
```bash
python scripts/evaluate.py \
    --model-path experiments/your_experiment/model/ \
    --test-data data/processed/test.jsonl
```

**Output:**
```
EVALUATION RESULTS
============================================================
F1 Score:  0.9123
Precision: 0.9245
Recall:    0.9004

Detailed Classification Report:
============================================================
              precision    recall  f1-score   support

      PERSON       0.94      0.92      0.93       245
     ADDRESS       0.89      0.87      0.88       189
       EMAIL       0.98      0.99      0.99       156
       PHONE       0.97      0.96      0.97       167
       PESEL       0.99      0.98      0.99       178
         NIP       0.96      0.95      0.96       134
       REGON       0.95      0.94      0.95       112

   micro avg       0.92      0.90      0.91      1181
   macro avg       0.95      0.94      0.95      1181
weighted avg       0.95      0.90      0.92      1181
```

---

## ⚙️ Konfiguracja

### training_config.yaml - szczegółowe wyjaśnienie
```yaml
model:
  name: "allegro/herbert-base-cased"
  # Opcje: herbert-base-cased (110M), herbert-large-cased (340M)
  num_labels: 10
  # Liczba klas NER (nie zmieniaj bez aktualizacji model_config.yaml)

data:
  max_length: 128
  # Max tokens per example. Zwiększ do 256/512 dla dłuższych dokumentów
  # UWAGA: Większa długość = więcej VRAM

training:
  num_train_epochs: 5
  # Typowo 3-5 epok wystarcza. Więcej = ryzyko overfittingu
  
  per_device_train_batch_size: 16
  # Zmniejsz do 8 lub 4 jeśli dostajesz OOM (Out of Memory)
  # Zwiększ gradient_accumulation_steps żeby skompensować
  
  learning_rate: 2.0e-5
  # Standard dla BERT fine-tuning. Możesz eksperymentować z 1e-5 do 5e-5
  
  weight_decay: 0.01
  # Regularization - zapobiega overfittingowi
  
  warmup_steps: 500
  # Ile steps na warmup LR. ~10% total steps to dobry start
  
  fp16: true
  # Mixed precision - DUŻO szybsze na GPU z Tensor Cores
  # Ustaw false jeśli masz problemy z numeryczną stabilnością
  
  gradient_accumulation_steps: 2
  # Effective batch = batch_size * gradient_accumulation_steps
  # Zwiększ jeśli masz małe GPU memory
  
  early_stopping_patience: 3
  # Stop training jeśli val metric nie poprawia się przez 3 epoki

seed: 42
# Ustaw dla reproducibility
```

### model_config.yaml - Label definitions

**Nie zmieniaj tego pliku chyba że:**
- Dodajesz nowe typy entities
- Zmieniasz BIO tagging scheme

---

## 🐛 Troubleshooting

### Problem 1: Out of Memory (OOM)

**Symptom:**
```
RuntimeError: CUDA out of memory. Tried to allocate X.XX GiB
```

**Rozwiązania:**
```yaml
# Solution A: Zmniejsz batch size
per_device_train_batch_size: 8  # było 16

# Solution B: Zwiększ gradient accumulation
gradient_accumulation_steps: 4  # było 2

# Solution C: Zmniejsz max_length
max_length: 64  # było 128

# Solution D: Wyłącz mixed precision (ostateczność)
fp16: false
```

### Problem 2: Loss nie spada

**Symptom:**
```
Epoch 1: loss=2.5
Epoch 2: loss=2.4
Epoch 3: loss=2.4  # Stuck!
```

**Możliwe przyczyny i rozwiązania:**

1. **Learning rate za niski** - zwiększ do 3e-5 lub 5e-5
2. **Data quality** - sprawdź czy labels są poprawnie aligned
3. **Model za mały dla danych** - spróbuj herbert-large-cased
```python
# Debug data quality
from src.training.dataset import NERDataset

dataset = NERDataset("data/processed/train.jsonl", tokenizer, label2id, 128)
example = dataset[0]

print("Input IDs:", example['input_ids'])
print("Labels:", example['labels'])
# Sprawdź czy labels mają sens (-100 dla special tokens, reszta 0-9)
```

### Problem 3: Overfitting

**Symptom:**
```
Epoch 3: train_loss=0.1, val_loss=0.5  # Duża różnica!
Epoch 4: train_loss=0.05, val_loss=0.7  # Val loss rośnie!
```

**Rozwiązania:**
```yaml
# Solution A: Więcej regularization
weight_decay: 0.05  # było 0.01

# Solution B: Early stopping
early_stopping_patience: 2  # było 3

# Solution C: Więcej danych
# Wygeneruj więcej przykładów (5000-10000)

# Solution D: Data augmentation
# Dodaj różnorodność w templates
```

### Problem 4: Low F1 score (< 0.80)

**Możliwe przyczyny:**

1. **Mało danych** - wygeneruj więcej (min 3000)
2. **Złe label alignment** - sprawdź dataset.py logic
3. **Za krótki trening** - zwiększ epochs do 7-10
4. **Model nie pasuje** - spróbuj inny base model

**Debug checklist:**
```bash
# 1. Sprawdź data quality
python scripts/generate_data.py --num-examples 100
head -5 data/processed/train.jsonl  # Inspect manually

# 2. Test na małym datasecie (szybki debug)
python scripts/train.py --config config/training_config.yaml
# Sprawdź czy train F1 osiąga > 0.95 (jeśli nie, problem z kodem)

# 3. Detailed evaluation
python scripts/evaluate.py --model-path experiments/.../model/
# Sprawdź per-class metrics - która klasa jest słaba?
```

### Problem 5: Training bardzo wolny

**Na CPU:**
- Oczekiwany czas: 2-3 godziny dla 3000 przykładów
- Rozwiązanie: Użyj GPU lub zmniejsz dataset do 1000 przykładów dla testów

**Na GPU ale wciąż wolny:**
```yaml
# Check 1: Czy używa GPU?
# W logs powinno być: "device: cuda:0"

# Check 2: Włącz mixed precision
fp16: true

# Check 3: Zwiększ batch size (jeśli masz VRAM)
per_device_train_batch_size: 32

# Check 4: Zmniejsz logging
logging_steps: 200  # było 50
```

---

## 📊 Performance Benchmarks

### Oczekiwane rezultaty

**Dla 3000 przykładów synthetic data:**

| Metric | Wartość | Opis |
|--------|---------|------|
| Train F1 | 0.95-0.98 | Powinien być wysoki |
| Val F1 | 0.88-0.93 | Główna metryka |
| Test F1 | 0.85-0.92 | Production metric |
| Training time (RTX 4080) | 30-60 min | 5 epochs |
| Training time (CPU) | 2-3 hours | 5 epochs |
| Inference (GPU) | ~50ms/doc | Single document |
| Inference (CPU) | ~200ms/doc | Single document |
| Model size | ~450 MB | herbert-base |

### Per-class performance (expected)

| Entity Type | F1 Score | Notes |
|-------------|----------|-------|
| PESEL | 0.95-0.99 | Najłatwiejszy (fixed format) |
| NIP | 0.94-0.98 | Fixed format + checksum |
| REGON | 0.93-0.97 | Fixed format |
| EMAIL | 0.96-0.99 | Prosty pattern |
| PHONE | 0.94-0.97 | Różne formaty |
| PERSON | 0.88-0.93 | Trudniejszy (kontekst) |
| ADDRESS | 0.85-0.90 | Najtrudniejszy (długie, złożone) |

### Hardware requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 10GB
- Training time: 2-3 hours

**Rekomendowane:**
- GPU: RTX 3060 or better (6GB+ VRAM)
- RAM: 16GB
- Disk: 20GB (SSD)
- Training time: 30-60 minutes

**Optimal (Twoja konfiguracja):**
- GPU: RTX 4080 (16GB VRAM)
- RAM: 32GB
- Training time: 20-30 minutes
- Możesz trenować większe modele (herbert-large) lub większe batch sizes

---

## 🎯 Next Steps

Po zakończeniu podstawowego treningu, rozważ:

### 1. LoRA Fine-tuning
- Szybszy trening
- Mniejsze modele
- Unikanie catastrophic forgetting

### 2. Model Quantization
- int8 quantization dla production
- 4x mniejszy model
- 2-3x szybszy inference

### 3. Więcej danych
- Manual annotation dla edge cases
- Data augmentation
- Integration z real documents

### 4. Advanced metrics
- Confusion matrix analysis
- Error analysis
- A/B testing framework

### 5. Production deployment
- ONNX export
- API server
- Monitoring dashboard

---

## 📞 Support

- Full error message + stack trace
- Config file (`training_config.yaml`)
- System info (GPU, CUDA version, Python version)
- Steps to reproduce

---

## 📝 License

MIT License - see LICENSE file for details