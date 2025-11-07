# 📊 Guide du Système de Logging Automatisé

Le système de logging a été entièrement automatisé pour capturer les métriques de training, générer les graphiques et archiver les paramètres sans intervention manuelle.

## 🎯 Fonctionnalités

### ✅ Automatique
- ✅ **Capture automatique** des logs de training en temps réel
- ✅ **Sauvegarde automatique** des paramètres au démarrage
- ✅ **Génération automatique** des graphiques à la fin
- ✅ **Résumé textuel** du training avec statistiques
- ✅ **Archivage de la config YAML** utilisée

### 📁 Fichiers Générés

À la fin du fine-tuning, le répertoire de sortie contient automatiquement :

```
Apertus-FT/output/apertus_lora_combined_20251107_123456/
├── config_backup/
│   └── sft_lora_combined.yaml        # Config YAML utilisée
├── training_parameters.json          # Tous les paramètres de training
├── training_logs.jsonl               # Logs bruts (format ligne par ligne)
├── training_logs.json                # Logs en JSON complet
├── training_config.json              # Config détaillée du trainer
├── training_metrics.png              # Graphiques complets (6 métriques)
├── training_loss.png                 # Graphique focus sur la loss
├── training_summary.txt              # Résumé textuel
└── [modèle et autres fichiers...]
```

## 🚀 Utilisation

### Lancement Standard

```bash
# Activer l'environnement
source apertus/bin/activate

# Lancer le fine-tuning (le logging est automatique)
apertus sft configs/sft_lora_combined.yaml
```

**Aucune action manuelle nécessaire !** Le système :
1. ✅ Crée un dossier avec timestamp
2. ✅ Sauvegarde les paramètres au démarrage
3. ✅ Capture les logs en temps réel
4. ✅ Génère les graphiques à la fin
5. ✅ Crée un résumé textuel

### Sortie Console

Le système affiche des messages clairs à chaque étape :

```
📁 Output directory: Apertus-FT/output/apertus_lora_combined_20251107_123456
✅ Config YAML sauvegardée: .../config_backup/sft_lora_combined.yaml
✅ Paramètres sauvegardés: .../training_parameters.json

══════════════════════════════════════════════════════════════════
🚀 DÉBUT DU FINE-TUNING
══════════════════════════════════════════════════════════════════
📁 Output dir: Apertus-FT/output/apertus_lora_combined_20251107_123456
🕐 Start time: 2025-11-07 12:34:56
✅ Config sauvegardée: .../training_config.json

[... training en cours ...]

══════════════════════════════════════════════════════════════════
✅ FIN DU FINE-TUNING
══════════════════════════════════════════════════════════════════
🕐 End time: 2025-11-07 14:12:34
⏱️  Duration: 1:37:38
📊 Total steps: 1938

✅ Logs sauvegardés: .../training_logs.jsonl
✅ Logs sauvegardés: .../training_logs.json

📈 Génération des graphiques...
  ✓ .../training_metrics.png
  ✓ .../training_loss.png
✅ Graphiques générés

✅ Résumé sauvegardé: .../training_summary.txt
```

## 📊 Visualisation des Graphiques

### Automatique (Recommandé)

Les graphiques sont générés automatiquement à la fin du training.

### Manuel (Si Nécessaire)

Si vous voulez regénérer les graphiques :

```bash
# Utiliser le dernier dossier de training
python plot_training_logs.py

# Spécifier un dossier spécifique
python plot_training_logs.py --output-dir Apertus-FT/output/apertus_lora_combined_20251107_123456

# Utiliser un fichier de log spécifique (ancien format)
python plot_training_logs.py --log-file training_loss_logs.txt
```

## 📈 Métriques Capturées

### Training Loss
- Évolution par step
- Évolution par epoch
- Statistiques (min, max, finale, amélioration)

### Token Accuracy
- Précision moyenne des tokens
- Évolution au cours du training

### Learning Rate
- Schedule complet
- Valeur maximale et finale

### Gradient Norm
- Stabilité du gradient
- Détection de valeurs anormales

### Entropy
- Confiance du modèle
- Évolution de l'incertitude

## 🗂️ Format des Fichiers

### training_parameters.json

```json
{
  "timestamp": "20251107_123456",
  "model": {
    "name_or_path": "swiss-ai/Apertus-8B-Instruct-2509",
    "dtype": "torch.bfloat16",
    "attn_implementation": "flash_attention_2"
  },
  "dataset": {
    "name": "./data/custom_mix_dataset_hf",
    "train_split": "train",
    "test_split": "test"
  },
  "training": {
    "learning_rate": 7e-05,
    "num_train_epochs": 1.0,
    "per_device_train_batch_size": 8,
    "gradient_accumulation_steps": 4,
    ...
  }
}
```

### training_logs.jsonl

Format ligne par ligne (un JSON par ligne) :

```jsonl
{"step": 1, "epoch": 0.0, "loss": 1.7988, "grad_norm": 0.39, "learning_rate": 0.0, ...}
{"step": 2, "epoch": 0.01, "loss": 1.7622, "grad_norm": 0.40, "learning_rate": 2.5e-07, ...}
...
```

### training_summary.txt

Résumé textuel lisible :

```
======================================================================
RÉSUMÉ DU FINE-TUNING
======================================================================

📅 Début:     2025-11-07 12:34:56
📅 Fin:       2025-11-07 14:12:34
⏱️  Durée:     1:37:38

📊 MÉTRIQUES
----------------------------------------------------------------------
Total steps:          1938

Loss:
  - Initiale:         1.7988
  - Finale:           1.1013
  - Minimale:         0.9683
  - Maximale:         1.7988
  - Amélioration:     38.78%

Accuracy:
  - Initiale:         0.6046
  - Finale:           0.7079
  - Amélioration:     17.08%
...
```

## 🔧 Personnalisation

### Modifier les Métriques Capturées

Éditez `training_logger.py`, méthode `on_log()` :

```python
def on_log(self, args, state, control, logs=None, **kwargs):
    if logs is None:
        return

    if 'loss' in logs and state.global_step > 0:
        log_entry = {
            'step': state.global_step,
            'epoch': state.epoch,
            'loss': logs.get('loss', None),
            # Ajouter vos métriques personnalisées ici
            'custom_metric': logs.get('custom_metric', None),
        }
```

### Ajouter des Graphiques Personnalisés

Éditez `training_logger.py`, méthode `_generate_plots()` :

```python
def _generate_plots(self):
    # ... code existant ...

    # Ajouter votre graphique personnalisé
    self._plot_custom_metric(data)
```

## 🐛 Troubleshooting

### Erreur : "ModuleNotFoundError: No module named 'training_logger'"

**Solution** : Assurez-vous d'être dans le bon répertoire :
```bash
cd /path/to/apertus-finetuning-recipes
source apertus/bin/activate
```

### Erreur : "ModuleNotFoundError: No module named 'matplotlib'"

**Solution** : Matplotlib devrait déjà être installé. Si ce n'est pas le cas :
```bash
source apertus/bin/activate
uv pip install matplotlib
```

### Les graphiques ne sont pas générés

**Vérifications** :
1. Le training s'est-il terminé normalement ?
2. Y a-t-il un fichier `training_logs.jsonl` ?
3. Y a-t-il des données dans le fichier ?

```bash
# Vérifier le dernier dossier
ls -lh Apertus-FT/output/apertus_lora_combined_*/training_logs.jsonl

# Compter les lignes
wc -l Apertus-FT/output/apertus_lora_combined_*/training_logs.jsonl
```

### Regénérer les graphiques manuellement

```bash
python plot_training_logs.py --output-dir Apertus-FT/output/apertus_lora_combined_20251107_123456
```

## 💡 Conseils

### Pour le Débogage

1. **Vérifier les logs en temps réel** :
   ```bash
   tail -f Apertus-FT/output/apertus_lora_combined_*/training_logs.jsonl
   ```

2. **Comparer deux trainings** :
   ```bash
   python plot_training_logs.py --output-dir Apertus-FT/output/apertus_lora_combined_20251107_123456
   python plot_training_logs.py --output-dir Apertus-FT/output/apertus_lora_combined_20251107_145678
   ```

3. **Analyser les paramètres** :
   ```bash
   cat Apertus-FT/output/apertus_lora_combined_*/training_parameters.json | jq .
   ```

### Pour l'Archivage

Tous les fichiers nécessaires pour reproduire le training sont sauvegardés :

```bash
# Créer une archive d'un training
cd Apertus-FT/output
tar -czf apertus_lora_combined_20251107_123456.tar.gz apertus_lora_combined_20251107_123456/

# Extraire plus tard
tar -xzf apertus_lora_combined_20251107_123456.tar.gz
```

## 📚 Fichiers Associés

- **`training_logger.py`** - Callback principal de logging
- **`plot_training_logs.py`** - Script de génération de graphiques
- **`sft_train.py`** - Script de training modifié

## 🔄 Migration depuis l'Ancien Système

### Ancien Workflow (Manuel)

```bash
# 1. Copier manuellement les logs de la console
# 2. Coller dans un fichier .txt
# 3. Modifier plot_training_logs.py avec le bon chemin
# 4. Exécuter plot_training_logs.py
python plot_training_logs.py
```

### Nouveau Workflow (Automatique)

```bash
# 1. Lancer le training
apertus sft configs/sft_lora_combined.yaml

# C'est tout ! Les logs, graphiques et résumés sont générés automatiquement
```

### Compatibilité

Le nouveau système est **rétro-compatible** avec l'ancien format :

```bash
# Utiliser l'ancien fichier de logs
python plot_training_logs.py --log-file training_loss_logs.txt
```

## ✅ Checklist Post-Training

Après chaque fine-tuning, vérifiez que vous avez :

- [ ] `training_parameters.json` - Paramètres sauvegardés
- [ ] `config_backup/` - Config YAML archivée
- [ ] `training_logs.jsonl` - Logs bruts
- [ ] `training_logs.json` - Logs JSON
- [ ] `training_metrics.png` - Graphiques complets
- [ ] `training_loss.png` - Graphique loss
- [ ] `training_summary.txt` - Résumé

Si un fichier manque, utilisez :
```bash
python plot_training_logs.py --output-dir <output_dir>
```

---

**Version** : 2.0 - Logging Automatisé
**Dernière mise à jour** : 2025-11-07
