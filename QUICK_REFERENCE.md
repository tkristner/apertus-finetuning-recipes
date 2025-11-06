# ⚡ Aide-Mémoire Rapide - test.py

> **Note:** Utilisez `./test.sh` ou `python3 test.py` selon votre système

## 🎯 Les 4 Commandes Essentielles

### 1️⃣ Question Libre sur Votre Modèle
```bash
./test.sh --model Apertus-FT/output/apertus_lora_custom_001 --question "Votre question"
```

### 2️⃣ Comparer BASE vs Votre Modèle (Question Libre)
```bash
./test.sh --model Apertus-FT/output/apertus_lora_custom_001 --compare --question "Votre question"
```

### 3️⃣ Benchmark Complet sur Votre Modèle
```bash
./test.sh --model Apertus-FT/output/apertus_lora_custom_001 --benchmark
```

### 4️⃣ Comparer BASE vs Votre Modèle (Benchmark Complet) ⭐
```bash
./test.sh --model Apertus-FT/output/apertus_lora_custom_001 --compare --benchmark
```

---

## 📝 Syntaxe Générale

```
python test.py [MODÈLE] [TYPE_TEST] [OPTIONS]
```

### MODÈLE (obligatoire, choisir un)
- `--model <chemin>` → Votre modèle fine-tuné
- `--base` → Modèle de base (sans fine-tuning)

### TYPE_TEST (obligatoire, choisir un)
- `--question "texte"` → Question libre
- `--benchmark` → 9 questions prédéfinies

### OPTIONS (optionnelles)
- `--compare` → Compare BASE vs modèle fine-tuné
- `--output <fichier>` → Sauvegarde les résultats (avec --benchmark)
- `--max-tokens <N>` → Longueur max des réponses (défaut: 4096)

---

## 🔄 Exemples par Cas d'Usage

### Test Rapide
```bash
python test.py --model <chemin> --question "Bonjour!"
```

### Vérifier l'Impact du Fine-tuning
```bash
python test.py --model <chemin> --compare --question "Explique le RGPD"
```

### Évaluation Complète
```bash
python test.py --model <chemin> --compare --benchmark
```

### Tester le Modèle de Base
```bash
python test.py --base --question "Qu'est-ce que LoRA?"
```

---

## 📊 Les 9 Questions du Benchmark

1. **Logique** - Syllogisme
2. **Maths** - Problème de trains
3. **Analyse** - IA médicale
4. **Créativité** - Science-fiction
5. **Technique** - LoRA vs Full FT
6. **Éthique** - Dilemme du tramway
7. **RGPD** - Droit à l'effacement (niveau DPO)
8. **Code** - Crible d'Ératosthène
9. **Multilingue** - EN + FR

---

## 💡 Workflow Recommandé

```bash
# 1. Test simple
python test.py --model <chemin> --question "Test rapide"

# 2. Comparaison ciblée
python test.py --model <chemin> --compare --question "Question importante"

# 3. Évaluation complète
python test.py --model <chemin> --compare --benchmark
```

---

## 🆘 Aide

```bash
python test.py --help
```

Voir **TEST_README.md** pour le guide complet.
