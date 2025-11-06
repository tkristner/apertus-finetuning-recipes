# 📦 Anciens Scripts (Archivés)

Ces scripts ont été remplacés par le nouveau script unifié **`test.py`**.

## Migration

| Ancien Script | Nouvelle Commande |
|---------------|-------------------|
| `python test_model.py <model> "question"` | `python test.py --model <model> --question "question"` |
| `python test_base_model.py "question"` | `python test.py --base --question "question"` |
| `./benchmark_model.sh <model>` | `python test.py --model <model> --benchmark` |
| `./compare_models.sh BASE <model>` | `python test.py --model <model> --compare --question "..."` |
| `./compare_models.sh BASE <model>` (benchmark) | `python test.py --model <model> --compare --benchmark` |

## Pourquoi le Changement?

✅ **Un seul script** au lieu de 5+
✅ **Syntaxe cohérente** et prévisible
✅ **Plus facile à maintenir**
✅ **Moins de confusion**

## Documentation

Voir **`TEST_README.md`** dans le répertoire parent pour le guide complet.

## Conservation

Ces scripts sont conservés pour référence mais ne sont plus maintenus.
