# 📏 Guide du Context Size (Longueur de Séquence)

## Qu'est-ce que le Context Size?

Le **context size** (ou `max_length`) définit la **longueur maximale** d'une séquence (prompt + réponse) pendant le fine-tuning, mesurée en **tokens**.

---

## 🔧 Configuration

### **Paramètre dans les fichiers YAML**

```yaml
max_length: 4096  # Context size en tokens
```

**Fichiers concernés:**
- `configs/sft_lora_custom.yaml`
- `configs/sft_lora_combined.yaml`
- Tous les fichiers de configuration de fine-tuning

---

## 📊 Valeurs Recommandées

| Context Size | Usage | Avantages | Inconvénients |
|--------------|-------|-----------|---------------|
| **1024** | Réponses courtes | Rapide, moins de VRAM | Tronque les longs textes |
| **2048** | Standard | Bon équilibre | Peut tronquer analyses longues |
| **4096** ✅ | Recommandé | Supporte analyses détaillées | Plus de VRAM nécessaire |
| **8192** | Très long | Aucune troncature | Beaucoup de VRAM, plus lent |

### **Configuration Actuelle: 4096 tokens**

C'est un bon compromis pour:
- ✅ Analyses RGPD détaillées
- ✅ Problèmes mathématiques avec raisonnement étape par étape
- ✅ Réponses complètes sans troncature
- ✅ Compatible avec la plupart des GPUs (24GB VRAM)

---

## 🎯 Modèle de Base Apertus

Le modèle `swiss-ai/Apertus-8B-Instruct-2509` supporte:
- **Context window:** 8192 tokens (maximum)
- **Recommandé pour fine-tuning:** 4096 tokens

---

## 💾 Impact sur la VRAM

| Context Size | Batch Size 4 | Batch Size 8 | VRAM Estimée |
|--------------|--------------|--------------|--------------|
| 1024 | ✅ | ✅ | ~12 GB |
| 2048 | ✅ | ✅ | ~16 GB |
| 4096 | ✅ | ⚠️ | ~20-24 GB |
| 8192 | ⚠️ | ❌ | ~40+ GB |

**Note:** Avec `gradient_checkpointing: true`, la VRAM est réduite d'environ 30-40%.

---

## 🔍 Vérifier la Longueur de Vos Données

### **Script de Vérification**

```python
from transformers import AutoTokenizer
import json

tokenizer = AutoTokenizer.from_pretrained("swiss-ai/Apertus-8B-Instruct-2509")

# Charger votre dataset
with open("./data/combined_dataset/train.jsonl", "r") as f:
    lengths = []
    for line in f:
        data = json.loads(line)
        messages = data["messages"]
        
        # Appliquer le chat template
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        tokens = tokenizer.encode(text)
        lengths.append(len(tokens))
    
    print(f"📊 Statistiques de longueur (tokens):")
    print(f"   - Min: {min(lengths)}")
    print(f"   - Max: {max(lengths)}")
    print(f"   - Moyenne: {sum(lengths)/len(lengths):.0f}")
    print(f"   - Médiane: {sorted(lengths)[len(lengths)//2]}")
    
    # Pourcentage tronqué selon différents max_length
    for max_len in [1024, 2048, 4096, 8192]:
        truncated = sum(1 for l in lengths if l > max_len)
        pct = truncated / len(lengths) * 100
        print(f"   - Tronqués avec max_length={max_len}: {truncated} ({pct:.1f}%)")
```

---

## ⚙️ Ajuster le Context Size

### **Augmenter (pour textes plus longs)**

```yaml
max_length: 8192  # Double le context
```

**Attention:**
- ⚠️ Nécessite plus de VRAM
- ⚠️ Training plus lent
- ⚠️ Peut nécessiter de réduire `per_device_train_batch_size`

### **Réduire (pour économiser VRAM)**

```yaml
max_length: 2048  # Réduit de moitié
```

**Conséquences:**
- ✅ Moins de VRAM
- ✅ Training plus rapide
- ❌ Textes longs tronqués

---

## 🎯 Recommandations par Cas d'Usage

### **1. Dataset RGPD uniquement**
```yaml
max_length: 4096  # Analyses détaillées
```

### **2. Dataset Math uniquement**
```yaml
max_length: 2048  # Problèmes courts
```

### **3. Dataset Combiné (RGPD + Math)**
```yaml
max_length: 4096  # Supporte les deux
```

### **4. GPU avec peu de VRAM (<16GB)**
```yaml
max_length: 2048
per_device_train_batch_size: 2
gradient_accumulation_steps: 16
gradient_checkpointing: true
```

### **5. GPU puissant (>40GB)**
```yaml
max_length: 8192
per_device_train_batch_size: 8
```

---

## 🧪 Tester Différentes Valeurs

### **Méthode 1: Tester avec un petit dataset**

```bash
# Créer un petit subset pour test
head -n 100 ./data/combined_dataset/train.jsonl > ./data/test_subset/train.jsonl

# Tester avec max_length=2048
# Modifier le yaml, puis:
python sft_train.py configs/sft_lora_combined.yaml

# Observer la VRAM et la vitesse
```

### **Méthode 2: Calculer la VRAM nécessaire**

**Formule approximative:**
```
VRAM (GB) ≈ (model_size_GB × 1.5) + (batch_size × max_length × 0.002)
```

Pour Apertus-8B:
```
VRAM ≈ (16 GB × 1.5) + (4 × 4096 × 0.002)
VRAM ≈ 24 GB + 32.8 MB ≈ 24 GB
```

---

## 📝 Configuration Actuelle

### **`sft_lora_custom.yaml`**
```yaml
max_length: 4096
per_device_train_batch_size: 4
gradient_accumulation_steps: 8
gradient_checkpointing: true
```

**Effective batch size:** 4 × 8 = 32  
**VRAM estimée:** ~20-24 GB  
**Compatible avec:** RTX 3090, RTX 4090, A100 (24GB), L40S

### **`sft_lora_combined.yaml`**
```yaml
max_length: 4096
per_device_train_batch_size: 4
gradient_accumulation_steps: 8
gradient_checkpointing: true
```

**Même configuration** pour cohérence.

---

## ⚠️ Problèmes Courants

### **1. Out of Memory (OOM)**

**Symptôme:** `CUDA out of memory`

**Solutions:**
```yaml
# Option 1: Réduire max_length
max_length: 2048

# Option 2: Réduire batch size
per_device_train_batch_size: 2
gradient_accumulation_steps: 16  # Compenser

# Option 3: Activer gradient checkpointing
gradient_checkpointing: true
```

### **2. Textes Tronqués**

**Symptôme:** Réponses incomplètes dans le dataset

**Solutions:**
```yaml
# Augmenter max_length
max_length: 8192

# Ou filtrer les exemples trop longs avant le training
```

### **3. Training Très Lent**

**Symptôme:** <1 it/s

**Solutions:**
```yaml
# Réduire max_length
max_length: 2048

# Ou activer packing (si supporté)
packing: true
```

---

## 🔄 Relation avec le Script de Test

Le script `test.py` utilise `max_new_tokens` pour la **génération**:

```python
max_new_tokens=4096  # Tokens générés (réponse uniquement)
```

**Différence:**
- **`max_length` (training):** Prompt + Réponse
- **`max_new_tokens` (inference):** Réponse uniquement

**Cohérence recommandée:**
```yaml
# Training
max_length: 4096

# Test (dans test.py)
max_new_tokens: 4096  # Ou moins si prompt long
```

---

## 📊 Monitoring

### **Pendant le Training**

Surveillez dans les logs:
```
[INFO] Truncated sequences: 0/100 (0.0%)
```

Si beaucoup de troncature:
- ✅ Augmenter `max_length`
- ✅ Ou filtrer les exemples longs

### **Après le Training**

Testez avec des questions longues:
```bash
./test.sh --model <chemin> --question "$(cat long_question.txt)"
```

---

## 💡 Conseils

1. **Commencez avec 4096** - C'est un bon compromis
2. **Vérifiez vos données** - Calculez la longueur moyenne
3. **Surveillez la VRAM** - Ajustez si OOM
4. **Testez** - Lancez un petit training pour valider
5. **Documentez** - Notez le max_length utilisé pour chaque modèle

---

## 🚀 Quick Reference

| Objectif | max_length | Batch Size | VRAM |
|----------|------------|------------|------|
| **Rapide** | 2048 | 8 | ~16 GB |
| **Standard** ✅ | 4096 | 4 | ~24 GB |
| **Maximum** | 8192 | 2 | ~40 GB |

**Configuration actuelle: Standard (4096 tokens)** ✅
