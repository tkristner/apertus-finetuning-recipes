# 🧮 Guide MetaMathQA - Améliorer le Raisonnement Mathématique

## Problème Identifié

Les deux modèles (BASE et fine-tuné) donnent des **réponses incorrectes** sur le problème de trains:

### ❌ Réponse Correcte Attendue
**Question:** Un train part de Paris à 14h à 120 km/h. Un autre part de Lyon (450 km) à 14h30 à 100 km/h vers Paris. Quand se croisent-ils?

**Calcul correct:**
1. À 14h30, le train de Paris a déjà parcouru: 120 km/h × 0.5h = 60 km
2. Distance restante: 450 - 60 = 390 km
3. Vitesse d'approche: 120 + 100 = 220 km/h
4. Temps pour se croiser: 390 / 220 = 1.77 heures ≈ 1h46min
5. **Heure de croisement: 14h30 + 1h46 = 16h16**
6. **Distance de Paris: 60 + (120 × 1.77) = 272 km**

### ❌ Réponses Actuelles des Modèles
- **BASE:** 18h à 400 km (complètement faux)
- **FINE-TUNÉ:** 15h à 120 km (complètement faux)

## Solution: Intégrer MetaMathQA

MetaMathQA est un dataset de **395K problèmes mathématiques** avec raisonnement étape par étape.

---

## 🚀 Utilisation

### **Étape 1: Préparer MetaMathQA (20%)**

```bash
python prepare_metamath_dataset.py --ratio 0.2 --max-samples 10000
```

**Options:**
- `--ratio 0.2` → 20% du dataset (≈79K exemples, limité à 10K)
- `--max-samples 10000` → Maximum 10K exemples
- `--output ./data/metamath_subset` → Répertoire de sortie

**Résultat:**
- Crée `./data/metamath_subset/train.jsonl`
- ~10K exemples de problèmes mathématiques
- Format: Chat avec système prompt spécialisé en maths

### **Étape 2: Combiner avec Votre Dataset (80% Custom / 20% Math)**

```bash
python prepare_metamath_dataset.py --ratio 0.2 --max-samples 10000 --combine --metamath-ratio 0.2
```

**Résultat:**
- Crée `./data/combined_dataset/train.jsonl`
- **80% de votre dataset RGPD** (prioritaire)
- **20% de MetaMathQA** (pour améliorer les maths)
- Format unifié avec système prompt adapté

**Personnaliser le ratio:**
```bash
# 70% Custom / 30% Math
python prepare_metamath_dataset.py --combine --metamath-ratio 0.3

# 90% Custom / 10% Math
python prepare_metamath_dataset.py --combine --metamath-ratio 0.1

# 50% Custom / 50% Math
python prepare_metamath_dataset.py --combine --metamath-ratio 0.5
```

### **Étape 3: Configurer le Fine-tuning**

Créez ou modifiez `configs/sft_lora_combined.yaml`:

```yaml
# Model
model_name_or_path: swiss-ai/Apertus-8B-Instruct-2509
output_dir: Apertus-FT/output/apertus_lora_combined

# Dataset combiné (RGPD + Math)
dataset_name: ./data/combined_dataset
dataset_train_split: train
dataset_test_split: train  # Pas de split test pour l'instant
dataset_num_proc: 12

# Hyperparameters
learning_rate: 5.0e-5
gradient_checkpointing: true
num_train_epochs: 3.0  # Moins d'epochs car plus de données
logging_steps: 1
eval_strategy: steps
eval_steps: 100
save_strategy: steps
save_steps: 200
per_device_train_batch_size: 4
gradient_accumulation_steps: 8
max_grad_norm: 0.5

# LoRA
use_peft: true
lora_r: 32
lora_alpha: 64
lora_dropout: 0.05
lora_target_modules: all-linear

# Training
bf16: true
max_seq_length: 2048
packing: false

# Optimizer
warmup_ratio: 0.1
lr_scheduler_type: cosine
min_lr_ratio: 0.05
```

### **Étape 4: Lancer le Fine-tuning**

```bash
python sft_train.py configs/sft_lora_combined.yaml
```

---

## 📊 Composition du Dataset Combiné (Par Défaut)

| Source | Exemples | Pourcentage | Spécialisation |
|--------|----------|-------------|----------------|
| **Custom RGPD** | ~500 | **80%** | Protection des données, RGPD |
| **MetaMathQA** | ~125 | **20%** | Mathématiques, logique, raisonnement |
| **TOTAL** | ~625 | 100% | Multi-domaine |

**Note:** Le ratio est calculé automatiquement en fonction de votre dataset custom.
- Si vous avez 500 exemples custom et `--metamath-ratio 0.2`, le script ajoutera ~125 exemples MetaMathQA
- Vous gardez **tous vos exemples custom** et le script ajuste MetaMathQA pour atteindre le ratio cible

---

## 🎯 Avantages de MetaMathQA

✅ **Raisonnement étape par étape:** Chaque problème a une solution détaillée  
✅ **Diversité:** Algèbre, géométrie, arithmétique, logique  
✅ **Qualité:** Dataset créé par Meta, haute qualité  
✅ **Format cohérent:** Compatible avec votre pipeline  
✅ **Taille contrôlée:** 20% = ~10K exemples (pas trop volumineux)

---

## 📈 Résultats Attendus

### **Avant (modèle actuel):**
- ❌ Problème de trains: réponse complètement fausse
- ❌ Pas de raisonnement structuré
- ❌ Erreurs de calcul basiques

### **Après (avec MetaMathQA):**
- ✅ Raisonnement étape par étape
- ✅ Calculs corrects
- ✅ Meilleure compréhension des problèmes de maths
- ✅ **Conservation des capacités RGPD (80% du dataset)**

---

## 🔧 Personnalisation

### **Ajuster le Ratio MetaMathQA**

**Par défaut (80% Custom / 20% Math):**
```bash
python prepare_metamath_dataset.py --combine --metamath-ratio 0.2
```

**Plus de maths (70% Custom / 30% Math):**
```bash
python prepare_metamath_dataset.py --combine --metamath-ratio 0.3
```

**Moins de maths (90% Custom / 10% Math):**
```bash
python prepare_metamath_dataset.py --combine --metamath-ratio 0.1
```

**Équilibré (50% Custom / 50% Math):**
```bash
python prepare_metamath_dataset.py --combine --metamath-ratio 0.5
```

### **Système Prompt Personnalisé**

Éditez `prepare_metamath_dataset.py` ligne 52:
```python
"content": "You are a helpful AI assistant specialized in mathematics and logical reasoning. Provide step-by-step solutions."
```

### **Filtrer par Type de Problème**

MetaMathQA contient différents types. Pour filtrer:
```python
# Dans prepare_metamath_dataset.py, ajoutez un filtre:
if example.get("type") in ["algebra", "arithmetic"]:
    # Traiter seulement ces types
```

---

## 🧪 Tester le Nouveau Modèle

Après le fine-tuning:

```bash
# Test sur le problème de trains
./test.sh --model Apertus-FT/output/apertus_lora_combined_YYYYMMDD_HHMMSS \
    --question "Un train part de Paris à 14h et roule à 120 km/h. Un autre train part de Lyon (450 km de Paris) à 14h30 et roule à 100 km/h vers Paris. À quelle heure et à quelle distance de Paris se croiseront-ils?"

# Comparaison avec BASE
./test.sh --model Apertus-FT/output/apertus_lora_combined_YYYYMMDD_HHMMSS \
    --compare --benchmark
```

---

## 📝 Exemple de Sortie MetaMathQA

**Question:**
```
Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?
```

**Réponse (avec raisonnement):**
```
Step 1: Calculate total eggs laid per day: 16 eggs
Step 2: Calculate eggs used for breakfast: 3 eggs
Step 3: Calculate eggs used for muffins: 4 eggs
Step 4: Calculate remaining eggs: 16 - 3 - 4 = 9 eggs
Step 5: Calculate revenue: 9 eggs × $2 = $18

Answer: Janet makes $18 every day at the farmers' market.
```

---

## ⚠️ Considérations

### **Taille du Dataset**
- 10K exemples ≈ 2-3 heures de fine-tuning (selon GPU)
- Plus d'exemples = meilleur raisonnement mais plus long

### **Équilibre des Domaines**
- **Par défaut: 80% RGPD / 20% maths** - Conserve l'expertise RGPD tout en améliorant les maths
- Ajustez le ratio selon vos priorités avec `--metamath-ratio`

### **Système Prompt**
- MetaMathQA utilise un prompt spécialisé en maths
- Votre dataset RGPD utilise un prompt spécialisé en protection des données
- Le modèle apprendra à s'adapter selon le contexte

---

## 🎓 Workflow Complet

```bash
# 1. Préparer le dataset combiné (80% Custom / 20% Math par défaut)
python prepare_metamath_dataset.py --ratio 0.2 --max-samples 10000 --combine --metamath-ratio 0.2

# 2. Vérifier le dataset
ls -lh ./data/combined_dataset/train.jsonl

# 3. Créer la config (si pas déjà fait)
cp configs/sft_lora_custom.yaml configs/sft_lora_combined.yaml
# Éditer: dataset_name: ./data/combined_dataset

# 4. Lancer le fine-tuning
python sft_train.py configs/sft_lora_combined.yaml

# 5. Tester le nouveau modèle
./test.sh --model Apertus-FT/output/apertus_lora_combined_* --compare --benchmark
```

---

## 💡 Conseils

1. **Commencez petit:** 10K exemples suffisent pour voir l'amélioration
2. **Testez rapidement:** Utilisez `--question` pour tester le problème de trains
3. **Comparez:** Utilisez `--compare` pour voir la différence avec BASE
4. **Itérez:** Si pas assez bon, augmentez le ratio ou les epochs
5. **Documentez:** Notez les hyperparamètres qui fonctionnent

---

## 🚀 Quick Start

```bash
# Tout en une commande
python prepare_metamath_dataset.py --ratio 0.2 --max-samples 10000 --combine && \
python sft_train.py configs/sft_lora_combined.yaml
```

Votre modèle devrait maintenant résoudre correctement le problème de trains! 🎯
