# Guide: Fine-tuning avec vos propres datasets

## Format de votre dataset JSONL

Votre dataset contient des questions/réponses avec le format suivant:
```json
{
  "question": "Your question here...",
  "answers": [
    {
      "text": "The answer text...",
      "type": "chosen",
      "score": 1.0,
      "thinking_process": "...",
      "metadata": {...}
    }
  ],
  "source_page_number": 174
}
```

## Étapes pour utiliser votre dataset

### 1. Préparer votre dataset

Éditez `prepare_dataset.py` et modifiez le chemin vers votre fichier JSONL:

```python
jsonl_path = "path/to/your/dataset.jsonl"  # UPDATE THIS
```

Puis exécutez:

```bash
python prepare_dataset.py
```

Cela va:
- Charger votre JSONL
- Convertir au format chat messages (system/user/assistant)
- Créer un split train/test (90%/10% par défaut)
- Sauvegarder dans `./data/converted_dataset/`

### 2. Option A: Utiliser le dataset converti (Recommandé)

Utilisez la config `sft_lora_custom.yaml`:

```bash
python sft_train.py --config configs/sft_lora_custom.yaml
```

### 2. Option B: Charger directement depuis JSONL

Modifiez votre config YAML:

```yaml
# Au lieu de:
dataset_name: HuggingFaceH4/Multilingual-Thinking

# Utilisez:
dataset_name: path/to/your/file.jsonl
dataset_train_split: train
dataset_test_split: test
```

**Note**: Cette option nécessite que votre JSONL soit déjà au format "messages" attendu.

### 3. Option C: Upload sur HuggingFace Hub (Pour réutilisation)

```python
from datasets import load_from_disk

# Charger le dataset converti
dataset = load_from_disk("./data/converted_dataset")

# Upload sur HuggingFace Hub
dataset.push_to_hub("your-username/your-dataset-name")
```

Puis dans votre config:
```yaml
dataset_name: your-username/your-dataset-name
```

## Format attendu par le modèle

Le modèle Apertus attend des conversations au format:

```python
{
  "messages": [
    {"role": "system", "content": "System prompt..."},
    {"role": "user", "content": "User question..."},
    {"role": "assistant", "content": "Assistant response..."}
  ]
}
```

Le script `prepare_dataset.py` fait cette conversion automatiquement.

## Personnalisation

### Modifier le prompt système

Dans `prepare_dataset.py`, ligne ~35:

```python
{
    "role": "system",
    "content": "You are a helpful AI assistant specialized in data protection and privacy compliance."
}
```

### Utiliser les réponses "rejected" pour DPO

Si vous voulez faire du Direct Preference Optimization (DPO) au lieu de SFT, vous devrez:
1. Garder les paires chosen/rejected
2. Utiliser `DPOTrainer` au lieu de `SFTTrainer`
3. Adapter le format du dataset

### Ajuster le split train/test

Dans `prepare_dataset.py`:

```python
dataset = load_and_convert_dataset(
    jsonl_path, 
    train_split=0.95  # 95% train, 5% test
)
```

## Vérification

Avant de lancer l'entraînement, vérifiez votre dataset:

```python
from datasets import load_from_disk

dataset = load_from_disk("./data/converted_dataset")
print(f"Train: {len(dataset['train'])} examples")
print(f"Test: {len(dataset['test'])} examples")
print("\nExample:")
print(dataset['train'][0])
```

## Troubleshooting

### Erreur: "Column 'messages' not found"

Votre dataset n'est pas au bon format. Assurez-vous d'avoir exécuté `prepare_dataset.py`.

### Erreur: "Dataset too large"

Réduisez `per_device_train_batch_size` ou augmentez `gradient_accumulation_steps` dans votre config.

### CUDA Out of Memory

Options:
- Réduire `max_length` (ex: 2048 au lieu de 4096)
- Réduire `per_device_train_batch_size`
- Activer `gradient_checkpointing: true`
- Utiliser LoRA avec des rangs plus petits (ex: `lora_r: 4`)
