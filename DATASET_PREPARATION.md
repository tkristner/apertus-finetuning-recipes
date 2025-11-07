# Dataset Preparation Guide

## 📊 Option C - Mix Diversifié (Recommandé)

### Répartition
```
60% Cybersécurité:
  ├─ 40% All Sources Deduplicated (mix cyber optimal)
  └─ 20% GDPR/Privacy (all_DPO_sources)

40% Diversification:
  ├─ 25% Nvidia Science Reasoning
  ├─ 10% Code (CodeAlpaca)
  └─  5% Créatif/Chat (Dolly)
```

### Sources Utilisées

| Source | Fichier | Taille | Ratio | Description |
|--------|---------|--------|-------|-------------|
| **Cyber Dedup** | `my_datasets/all_sources_deduplicated.jsonl` | 125K | 40% | Mix optimal cybersécurité (CTF + RedTeam + Privacy) |
| **DPO Privacy** | `my_datasets/all_DPO_sources_0.95-dedup.jsonl` | 11K | 20% | Spécialisation GDPR/DPO |
| **Nvidia Science** | `my_datasets/100k_nvidia_science_reasoning_SFT_converted.jsonl` | 100K | 25% | Raisonnement scientifique avec CoT |
| **Code** | HuggingFace: `sahil2801/CodeAlpaca-20k` | 20K | 10% | Développement logiciel |
| **General** | HuggingFace: `databricks/databricks-dolly-15k` | 15K | 5% | Chat général et créativité |

## 🚀 Utilisation

### 1. Créer le Dataset

```bash
# Activer l'environnement
source apertus/bin/activate

# Créer un dataset de 30,000 exemples (recommandé)
python3 prepare_custom_mix_dataset.py --target-total 30000

# Créer un dataset plus petit pour test
python3 prepare_custom_mix_dataset.py --target-total 5000 --output ./data/test_mix

# Avec seed personnalisé
python3 prepare_custom_mix_dataset.py --target-total 30000 --seed 12345
```

### 2. Validation Automatique

Le script valide automatiquement que chaque source a suffisamment d'exemples :

```bash
# Exemple : Trop d'exemples demandés
python3 prepare_custom_mix_dataset.py --target-total 200000
# ❌ VALIDATION ÉCHOUÉE
# ❌ dpo_privacy: Insuffisant (11,018 < 40,000)
```

**Limites actuelles** (basées sur les sources disponibles) :
- **Maximum théorique** : ~55K exemples (limité par dpo_privacy: 11K × 5 = 55K)
- **Recommandé** : 20K - 40K exemples

### 3. Configuration du Fine-tuning

Le dataset est automatiquement configuré dans `configs/sft_lora_combined.yaml` :

```yaml
dataset_name: ./data/custom_mix_dataset_hf
```

### 4. Lancer le Fine-tuning

```bash
apertus sft configs/sft_lora_combined.yaml
```

## 📁 Structure des Fichiers Générés

```
data/
├── custom_mix_dataset/
│   └── train.jsonl                    # Format JSONL brut (121MB pour 30K)
└── custom_mix_dataset_hf/
    ├── dataset_dict.json              # Métadonnées HuggingFace
    ├── train/                         # Split d'entraînement (90%)
    │   ├── data-00000-of-00001.arrow
    │   ├── dataset_info.json
    │   └── state.json
    └── test/                          # Split de test (10%)
        ├── data-00000-of-00001.arrow
        ├── dataset_info.json
        └── state.json
```

## 🔍 Vérification du Dataset

### Statistiques Rapides

```bash
source apertus/bin/activate

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
        line = f.readline()
        data = json.loads(line)

        print(f'\n=== Exemple {i+1} - Source: {data.get(\"source\")} ===')
        for msg in data['messages']:
            print(f'{msg[\"role\"].upper()}: {msg[\"content\"][:100]}...')
"
```

## 🎯 Calcul des Nombres Cibles

Pour calculer combien d'exemples demander selon vos besoins :

| Total Cible | Cyber Dedup | DPO Privacy | Nvidia Science | Code | General |
|-------------|-------------|-------------|----------------|------|---------|
| 10,000 | 4,000 | 2,000 | 2,500 | 1,000 | 500 |
| 20,000 | 8,000 | 4,000 | 5,000 | 2,000 | 1,000 |
| 30,000 | 12,000 | 6,000 | 7,500 | 3,000 | 1,500 |
| 40,000 | 16,000 | 8,000 | 10,000 | 4,000 | 2,000 |
| 50,000 | 20,000 | 10,000 | 12,500 | 5,000 | 2,500 |

**⚠️ Limite DPO Privacy** : Maximum 11,018 exemples disponibles, donc le total ne peut pas dépasser **55,090 exemples** (11,018 ÷ 0.20).

## 🛠️ Scripts Disponibles

### 1. `prepare_custom_mix_dataset.py` (Option C - Recommandé)
Mix optimisé avec validation automatique et vos datasets custom.

**Usage** :
```bash
python3 prepare_custom_mix_dataset.py --target-total 30000
```

### 2. `prepare_diversified_dataset.py` (Option Générique)
Mix avec datasets HuggingFace publics (MetaMathQA, CodeAlpaca, Dolly).

**Usage** :
```bash
python3 prepare_diversified_dataset.py \
  --cybersec my_datasets/all_DPO_sources_0.95-dedup.jsonl \
  --target-total 10000
```

### 3. Scripts Legacy
- `prepare_dataset.py` - Conversion dataset GDPR simple
- `prepare_metamath_dataset.py` - Préparation MetaMathQA
- `prepare_combined_dataset.py` - Combinaison GDPR + MetaMathQA

## 📈 Monitoring du Training

Après le fine-tuning, visualisez les métriques :

```bash
python3 plot_training_logs.py
```

Génère :
- `training_metrics.png` - Vue d'ensemble (loss, accuracy, learning rate, etc.)
- `training_loss.png` - Focus sur l'évolution de la loss

## 💡 Conseils

1. **Première fois** : Commencez avec 5K-10K exemples pour tester rapidement
2. **Production** : Utilisez 30K-40K exemples pour un modèle équilibré
3. **Maximum qualité** : Utilisez 50K+ exemples si vous avez plus de données DPO
4. **Seed fixe** : Gardez le même seed (`--seed 42`) pour la reproductibilité

## 🔧 Personnalisation des Ratios

Si vous voulez ajuster les ratios, modifiez dans `prepare_custom_mix_dataset.py` :

```python
sources = [
    DatasetSource(name="cyber_dedup", path="...", ratio=0.40),  # 40%
    DatasetSource(name="dpo_privacy", path="...", ratio=0.20),  # 20%
    DatasetSource(name="nvidia_science", path="...", ratio=0.25), # 25%
    DatasetSource(name="code", path="...", ratio=0.10),         # 10%
    DatasetSource(name="general", path="...", ratio=0.05),      # 5%
]
```

**Important** : Les ratios doivent sommer à 1.0 (100%).

## 📚 Format des Messages

Tous les exemples sont convertis au format standard :

```json
{
  "messages": [
    {"role": "system", "content": "System prompt adapté à la source..."},
    {"role": "user", "content": "Question de l'utilisateur..."},
    {"role": "assistant", "content": "Réponse du modèle..."}
  ],
  "source": "cyber_dedup|dpo_privacy|nvidia_science|code|general"
}
```

## 🎓 System Prompts par Source

| Source | System Prompt |
|--------|---------------|
| **cyber_dedup** | "You are an advanced cybersecurity expert specialized in offensive security, red teaming, and threat analysis." |
| **dpo_privacy** | "You are a helpful AI assistant specialized in data protection, privacy compliance, and GDPR regulations." |
| **nvidia_science** | "You are a helpful AI assistant specialized in scientific reasoning and problem-solving. Think step by step and provide detailed explanations." |
| **code** | "You are a helpful AI assistant specialized in software development and coding. Provide clear, efficient, and well-documented code solutions." |
| **general** | "You are a helpful, creative, and knowledgeable AI assistant. Provide informative and engaging responses." |

## 🐛 Troubleshooting

### Erreur : "Insuffisant (X < Y)"
**Problème** : Une source n'a pas assez d'exemples.
**Solution** : Réduisez `--target-total` ou ajoutez plus de données sources.

### Erreur : "Fichier introuvable"
**Problème** : Le chemin vers un dataset est incorrect.
**Solution** : Vérifiez les chemins avec `--cyber-dedup`, `--dpo-sources`, `--nvidia-reasoning`.

### Dataset vide ou incomplet
**Problème** : Format des données source incorrect.
**Solution** : Vérifiez que vos JSONL ont le bon format avec les exemples dans le script.

---

**Dernière mise à jour** : 2025-11-07
**Version** : Option C - Mix Diversifié avec Validation
