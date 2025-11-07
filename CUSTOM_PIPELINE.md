# 🔧 Custom Dataset Pipeline

Pipeline optimisée pour créer des datasets mixés personnalisés pour le fine-tuning d'Apertus.

## 🎯 Vue d'Ensemble

Cette pipeline implémente l'**Option C** - un mix diversifié optimisé :

```
60% Cybersécurité (expertise métier)
  ├─ 40% All Sources Deduplicated    # Mix cyber optimal
  └─ 20% GDPR/Privacy                 # Spécialisation DPO

40% Diversification (capacités générales)
  ├─ 25% Nvidia Science Reasoning     # Raisonnement scientifique
  ├─ 10% Code (CodeAlpaca)            # Développement logiciel
  └─  5% Général (Dolly)              # Chat général
```

## 🚀 Quick Start

### 1. Créer le dataset

```bash
# Activer l'environnement
source apertus/bin/activate

# Créer 30,000 exemples (recommandé pour production)
python3 prepare_custom_mix_dataset.py --target-total 30000

# Ou créer 5,000 exemples (pour test rapide)
python3 prepare_custom_mix_dataset.py --target-total 5000
```

### 2. Lancer le fine-tuning

```bash
# Le dataset est déjà configuré
apertus sft configs/sft_lora_combined.yaml
```

### 3. Visualiser les résultats

```bash
python3 plot_training_logs.py
```

## 📊 Sources de Données

| Source | Fichier | Taille | Ratio | Description |
|--------|---------|--------|-------|-------------|
| **Cyber Dedup** | `my_datasets/all_sources_deduplicated.jsonl` | 126K | 40% | Mix cybersécurité dédupliqué |
| **DPO Privacy** | `my_datasets/all_DPO_sources_0.95-dedup.jsonl` | 11K | 20% | GDPR/Privacy/DPO |
| **Nvidia Science** | `my_datasets/100k_nvidia_science_reasoning_SFT_converted.jsonl` | 100K | 25% | Raisonnement scientifique |
| **Code** | HuggingFace: `sahil2801/CodeAlpaca-20k` | 20K | 10% | Développement |
| **General** | HuggingFace: `databricks/databricks-dolly-15k` | 15K | 5% | Chat général |

**Limite** : Maximum ~55,000 exemples (limité par la source DPO Privacy : 11K ÷ 0.20 = 55K)

## ✅ Fonctionnalités

### Validation Automatique

Le script valide que chaque source a assez d'exemples **avant** de créer le dataset :

```bash
$ python3 prepare_custom_mix_dataset.py --target-total 200000

🔍 VALIDATION DES SOURCES
======================================================================
✅ cyber_dedup      - Requis: 80,000  | Disponible: 125,574
❌ dpo_privacy      - Requis: 40,000  | Disponible: 11,018  ❌
✅ nvidia_science   - Requis: 50,000  | Disponible: 100,000
✅ code             - Requis: 20,000  | Disponible: 20,000
✅ general          - Requis: 10,000  | Disponible: 15,000

❌ VALIDATION ÉCHOUÉE
❌ dpo_privacy: Insuffisant (11,018 < 40,000)

💡 Solutions:
   1. Réduire le nombre total d'exemples (--target-total)
   2. Ajuster les ratios
   3. Ajouter plus de données sources
```

### Conversion Automatique

Tous les formats sont convertis automatiquement vers le format `messages` :

```json
{
  "messages": [
    {"role": "system", "content": "System prompt adapté..."},
    {"role": "user", "content": "Question..."},
    {"role": "assistant", "content": "Réponse..."}
  ],
  "source": "cyber_dedup|dpo_privacy|nvidia_science|code|general"
}
```

## 🛠️ Usage Détaillé

### Options de Base

```bash
# Basique
python3 prepare_custom_mix_dataset.py --target-total 30000

# Avec répertoire de sortie personnalisé
python3 prepare_custom_mix_dataset.py \
  --target-total 30000 \
  --output ./data/my_custom_mix

# Avec seed pour reproductibilité
python3 prepare_custom_mix_dataset.py \
  --target-total 30000 \
  --seed 12345
```

### Options Avancées

```bash
# Spécifier les chemins des sources explicitement
python3 prepare_custom_mix_dataset.py \
  --target-total 30000 \
  --cyber-dedup /path/to/all_sources_deduplicated.jsonl \
  --dpo-sources /path/to/all_DPO_sources_0.95-dedup.jsonl \
  --nvidia-reasoning /path/to/nvidia_science.jsonl
```

### Paramètres

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `--target-total` | int | **Requis** - Nombre total d'exemples | - |
| `--output` | str | Répertoire de sortie | `./data/custom_mix_dataset` |
| `--seed` | int | Seed pour reproductibilité | `42` |
| `--cyber-dedup` | str | Chemin vers all_sources_deduplicated.jsonl | `my_datasets/...` |
| `--dpo-sources` | str | Chemin vers all_DPO_sources_0.95-dedup.jsonl | `my_datasets/...` |
| `--nvidia-reasoning` | str | Chemin vers nvidia science dataset | `my_datasets/...` |

## 📈 Calcul des Nombres

Pour calculer combien d'exemples seront utilisés par source :

| Total | Cyber Dedup (40%) | DPO (20%) | Nvidia (25%) | Code (10%) | General (5%) |
|-------|-------------------|-----------|--------------|------------|--------------|
| 5,000 | 2,000 | 1,000 | 1,250 | 500 | 250 |
| 10,000 | 4,000 | 2,000 | 2,500 | 1,000 | 500 |
| 20,000 | 8,000 | 4,000 | 5,000 | 2,000 | 1,000 |
| 30,000 | 12,000 | 6,000 | 7,500 | 3,000 | 1,500 |
| 40,000 | 16,000 | 8,000 | 10,000 | 4,000 | 2,000 |
| 50,000 | 20,000 | 10,000 | 12,500 | 5,000 | 2,500 |
| **55,000** | **22,000** | **11,000** ⚠️ | **13,750** | **5,500** | **2,750** |

⚠️ **Limite DPO** : Au-delà de 55K, la source DPO Privacy sera insuffisante.

## 📁 Structure Générée

```
data/
├── custom_mix_dataset/
│   └── train.jsonl              # Format JSONL brut (~4MB/1000 exemples)
└── custom_mix_dataset_hf/       # Format HuggingFace
    ├── dataset_dict.json
    ├── train/                   # 90% des données
    │   ├── data-00000-of-00001.arrow
    │   ├── dataset_info.json
    │   └── state.json
    └── test/                    # 10% des données
        ├── data-00000-of-00001.arrow
        ├── dataset_info.json
        └── state.json
```

## 🔍 Vérification du Dataset

### Statistiques

```bash
python3 -c "
import json
from collections import Counter

with open('data/custom_mix_dataset/train.jsonl', 'r') as f:
    data = [json.loads(line) for line in f if line.strip()]

sources = Counter(item.get('source', 'unknown') for item in data)
total = len(data)

print(f'Total: {total:,} exemples\n')
for src, count in sorted(sources.items()):
    print(f'{src:20} {count:6,} ({count/total*100:5.1f}%)')
"
```

### Visualiser des Exemples

```bash
python3 -c "
import json

with open('data/custom_mix_dataset/train.jsonl', 'r') as f:
    for i in range(3):
        data = json.loads(f.readline())
        print(f'\n=== {data.get(\"source\")} ===')
        for msg in data['messages']:
            print(f'{msg[\"role\"].upper()}: {msg[\"content\"][:80]}...')
"
```

## 🎓 System Prompts

Chaque source utilise un system prompt adapté à son domaine :

| Source | System Prompt |
|--------|---------------|
| **cyber_dedup** | "You are an advanced cybersecurity expert specialized in offensive security, red teaming, and threat analysis." |
| **dpo_privacy** | "You are a helpful AI assistant specialized in data protection, privacy compliance, and GDPR regulations." |
| **nvidia_science** | "You are a helpful AI assistant specialized in scientific reasoning and problem-solving. Think step by step..." |
| **code** | "You are a helpful AI assistant specialized in software development and coding..." |
| **general** | "You are a helpful, creative, and knowledgeable AI assistant..." |

## 🔧 Personnalisation

### Ajuster les Ratios

Pour modifier les ratios, éditez `prepare_custom_mix_dataset.py` (lignes 655-685) :

```python
sources = [
    DatasetSource(name="cyber_dedup", path="...", ratio=0.40),  # 40%
    DatasetSource(name="dpo_privacy", path="...", ratio=0.20),  # 20%
    DatasetSource(name="nvidia_science", path="...", ratio=0.25), # 25%
    DatasetSource(name="code", path="...", ratio=0.10),         # 10%
    DatasetSource(name="general", path="...", ratio=0.05),      # 5%
]
```

⚠️ **Important** : Les ratios doivent sommer à 1.0 (100%)

### Ajouter une Nouvelle Source

1. Créez un nouveau `DatasetSource` dans la fonction `main()`
2. Implémentez la logique de chargement dans `load_local_jsonl()` ou `load_huggingface_dataset()`
3. Ajustez les ratios pour qu'ils somment à 1.0

## 🐛 Troubleshooting

### ❌ "Insuffisant (X < Y)"

**Problème** : Une source n'a pas assez d'exemples.

**Solutions** :
```bash
# Option 1: Réduire le nombre total
python3 prepare_custom_mix_dataset.py --target-total 20000  # au lieu de 50000

# Option 2: Vérifier que les fichiers sources existent
ls -lh my_datasets/

# Option 3: Ajouter plus de données à la source problématique
```

### ❌ "Fichier introuvable"

**Problème** : Les chemins par défaut ne correspondent pas à votre structure.

**Solution** : Spécifiez les chemins explicitement :
```bash
python3 prepare_custom_mix_dataset.py \
  --target-total 30000 \
  --cyber-dedup /correct/path/to/all_sources_deduplicated.jsonl \
  --dpo-sources /correct/path/to/all_DPO_sources_0.95-dedup.jsonl
```

### ⚠️ Dataset vide ou incomplet

**Problème** : Format des données source incorrect.

**Solution** : Vérifiez le format de vos fichiers JSONL :
```bash
# Doit être du JSONL valide (1 JSON par ligne)
head -1 my_datasets/all_sources_deduplicated.jsonl | python3 -m json.tool
```

## 📊 Workflow Complet

### Développement / Test

```bash
# 1. Test rapide avec petit dataset
python3 prepare_custom_mix_dataset.py --target-total 1000

# 2. Vérifier les statistiques
python3 -c "
import json
with open('data/custom_mix_dataset/train.jsonl') as f:
    print(f'Total: {sum(1 for _ in f):,}')
"

# 3. Fine-tuning rapide (modifiez num_train_epochs: 0.1 dans la config)
apertus sft configs/sft_lora_combined.yaml

# 4. Vérifier que tout fonctionne
python3 plot_training_logs.py
```

### Production

```bash
# 1. Créer le dataset complet
python3 prepare_custom_mix_dataset.py --target-total 30000

# 2. Valider le dataset
python3 -c "
import json
from collections import Counter
with open('data/custom_mix_dataset/train.jsonl') as f:
    data = [json.loads(line) for line in f]
sources = Counter(d.get('source') for d in data)
print(f'Total: {len(data):,}')
for s, c in sources.items():
    print(f'{s}: {c:,} ({c/len(data)*100:.1f}%)')
"

# 3. Fine-tuning complet
apertus sft configs/sft_lora_combined.yaml

# 4. Analyser les résultats
python3 plot_training_logs.py
```

## 📚 Documentation Complète

- **[DATASET_PREPARATION.md](DATASET_PREPARATION.md)** - Guide détaillé sur les datasets
- **[README.md](README.md)** - Documentation générale Apertus
- **[configs/sft_lora_combined.yaml](configs/sft_lora_combined.yaml)** - Configuration du fine-tuning

## 🗂️ Scripts Legacy (Archivés)

Les anciens scripts ont été déplacés dans `.archive_old_scripts/` et ne sont plus utilisés :

- `prepare_dataset.py` - Conversion simple GDPR
- `prepare_metamath_dataset.py` - Préparation MetaMathQA seul
- `prepare_combined_dataset.py` - Mix GDPR + MetaMathQA
- `prepare_diversified_dataset.py` - Version test générique

**Ne pas utiliser ces scripts** - ils sont conservés uniquement pour référence historique.

## 💡 Conseils

1. **Première utilisation** : Commencez avec `--target-total 5000` pour tester rapidement
2. **Production** : Utilisez 30,000-40,000 exemples pour un équilibre optimal
3. **Reproductibilité** : Gardez le même `--seed` pour des résultats identiques
4. **Monitoring** : Utilisez `plot_training_logs.py` après chaque fine-tuning

## 📊 Métriques Attendues

Avec un dataset de 30K exemples et la config actuelle :

- **Training time** : ~4-6 heures sur GPU 40GB
- **Loss initiale** : ~1.8
- **Loss finale** : ~1.0-1.1
- **Token accuracy** : +10-15% d'amélioration
- **Taille du dataset** : ~240MB (HuggingFace format)

---

**Version** : 2.0 - Option C (Mix Optimisé)
**Dernière mise à jour** : 2025-11-07
**Script principal** : `prepare_custom_mix_dataset.py`
