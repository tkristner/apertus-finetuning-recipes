# 🧪 Guide de Test Unifié - Modèles Apertus

Un seul script pour tous vos besoins de test: **`test.py`**

---

## 📋 Syntaxe Générale

```bash
python test.py [--model <chemin> | --base] [--question <texte> | --benchmark] [--compare] [--output <fichier>]
```

---

## 🎯 Cas d'Usage

### **1. Question Libre sur Modèle Fine-tuné**

```bash
python test.py --model Apertus-FT/output/apertus_lora_custom_001 --question "Qu'est-ce que le RGPD?"
```

### **2. Question Libre sur Modèle de Base**

```bash
python test.py --base --question "Qu'est-ce que le RGPD?"
```

### **3. Benchmark Prédéfini (9 questions) sur Modèle Fine-tuné**

```bash
python test.py --model Apertus-FT/output/apertus_lora_custom_001 --benchmark
```

**Sauvegarde automatique dans:** `benchmark_YYYYMMDD_HHMMSS.txt`

### **4. Benchmark sur Modèle de Base**

```bash
python test.py --base --benchmark --output benchmark_base.txt
```

### **5. Comparaison BASE vs Fine-tuné avec Question Libre** ⭐

```bash
python test.py --model Apertus-FT/output/apertus_lora_custom_001 --compare --question "Explique-moi LoRA"
```

### **6. Comparaison BASE vs Fine-tuné avec Benchmark Complet** ⭐⭐⭐

```bash
python test.py --model Apertus-FT/output/apertus_lora_custom_001 --compare --benchmark
```

---

## 📊 Les 9 Questions du Benchmark

| # | Catégorie | Sujet |
|---|-----------|-------|
| 1 | Logique | Syllogisme (chats et animaux) |
| 2 | Mathématiques | Problème de trains |
| 3 | Analyse Critique | IA en médecine (avantages/inconvénients) |
| 4 | Créativité | Histoire de science-fiction |
| 5 | Technique | LoRA vs Fine-tuning complet |
| 6 | Éthique | Dilemme du tramway (voiture autonome) |
| 7 | RGPD | Droit à l'effacement et ML (niveau DPO) |
| 8 | Programmation | Crible d'Ératosthène en Python |
| 9 | Multilinguisme | Supervised vs Unsupervised (EN + FR) |

---

## 🔧 Options Avancées

### **Contrôler la Longueur des Réponses**

Par défaut: **4096 tokens** (permet des réponses complètes et détaillées)

Pour des réponses encore plus longues:
```bash
./test.sh --model <chemin> --question "..." --max-tokens 8192
```

Pour des réponses plus courtes (plus rapide):
```bash
./test.sh --model <chemin> --question "..." --max-tokens 1024
```

### **Sauvegarder les Résultats**

```bash
python test.py --model <chemin> --benchmark --output mes_resultats.txt
```

---

## 💡 Workflows Recommandés

### **Workflow 1: Test Rapide d'un Nouveau Fine-tuning**

```bash
# 1. Test avec une question simple
python test.py --model Apertus-FT/output/nouveau_modele --question "Bonjour, qui es-tu?"

# 2. Si satisfait, comparaison avec BASE
python test.py --model Apertus-FT/output/nouveau_modele --compare --question "Explique le fine-tuning"

# 3. Si toujours satisfait, benchmark complet
python test.py --model Apertus-FT/output/nouveau_modele --benchmark
```

### **Workflow 2: Évaluation Complète pour Production**

```bash
# Comparaison complète BASE vs Fine-tuné
python test.py --model Apertus-FT/output/mon_modele --compare --benchmark

# Résultats affichés à l'écran pour analyse immédiate
```

### **Workflow 3: Comparer Deux Configurations de Fine-tuning**

```bash
# Benchmark du modèle 1
python test.py --model Apertus-FT/output/config1 --benchmark --output results_config1.txt

# Benchmark du modèle 2
python test.py --model Apertus-FT/output/config2 --benchmark --output results_config2.txt

# Comparer manuellement les deux fichiers
diff results_config1.txt results_config2.txt
```

### **Workflow 4: Tester sur Vos Propres Questions**

```bash
# Question 1
python test.py --model <chemin> --compare --question "Question spécifique à votre domaine 1"

# Question 2
python test.py --model <chemin> --compare --question "Question spécifique à votre domaine 2"

# etc.
```

---

## 📈 Évaluation des Résultats

Après avoir lancé un benchmark, comparez avec `reference_answers.md`:

```bash
# 1. Lancer le benchmark
python test.py --model <chemin> --benchmark --output my_results.txt

# 2. Ouvrir côte à côte
# - my_results.txt (réponses du modèle)
# - reference_answers.md (réponses attendues)

# 3. Noter selon la grille (voir reference_answers.md)
```

**Grille de notation:**
- **90-100:** Expert - Prêt pour production
- **75-89:** Avancé - Bon pour la plupart des cas
- **60-74:** Intermédiaire - Nécessite améliorations
- **45-59:** Débutant - Réentraînement recommandé
- **<45:** Insuffisant - Revoir la stratégie

---

## 🎓 Exemples Concrets

### **Exemple 1: Premier test d'un modèle**

```bash
python test.py --model Apertus-FT/output/apertus_lora_custom_001 \
    --question "Explique-moi en 3 phrases ce qu'est le fine-tuning"
```

### **Exemple 2: Vérifier l'impact du fine-tuning**

```bash
python test.py --model Apertus-FT/output/apertus_lora_custom_001 \
    --compare \
    --question "Quels sont les principaux défis de l'IA aujourd'hui?"
```

### **Exemple 3: Évaluation complète**

```bash
python test.py --model Apertus-FT/output/apertus_lora_custom_001 \
    --compare \
    --benchmark
```

**Durée estimée:** ~30-45 minutes (9 questions × 2 modèles)

### **Exemple 4: Benchmark du modèle de base (référence)**

```bash
python test.py --base --benchmark --output benchmark_base_reference.txt
```

---

## 🆘 Aide et Exemples

Pour voir tous les exemples d'utilisation:

```bash
python test.py --help
```

---

## 📁 Fichiers Générés

```
apertus-finetuning-recipes/
├── benchmark_YYYYMMDD_HHMMSS.txt    # Résultats automatiques
├── my_results.txt                    # Résultats personnalisés (--output)
└── reference_answers.md              # Réponses de référence pour évaluation
```

---

## ⚡ Résumé des Commandes Essentielles

| Action | Commande |
|--------|----------|
| **Question libre sur fine-tuné** | `python test.py --model <chemin> --question "..."` |
| **Question libre sur BASE** | `python test.py --base --question "..."` |
| **Benchmark fine-tuné** | `python test.py --model <chemin> --benchmark` |
| **Comparer avec question** | `python test.py --model <chemin> --compare --question "..."` |
| **Comparer avec benchmark** ⭐ | `python test.py --model <chemin> --compare --benchmark` |

---

## 🔍 Différences avec l'Ancien Système

### **Avant (multiple scripts):**
- ❌ `test_model.py` pour fine-tuné
- ❌ `test_base_model.py` pour base
- ❌ `compare_models.sh` pour comparaison
- ❌ `benchmark_model.sh` pour benchmark
- ❌ `quick_test.sh` pour tests interactifs

### **Maintenant (un seul script):**
- ✅ `test.py` pour TOUT
- ✅ Syntaxe cohérente et unifiée
- ✅ Plus simple à utiliser
- ✅ Plus facile à maintenir

---

## 💡 Conseils

1. **Toujours commencer par une question libre** pour vérifier que le modèle fonctionne
2. **Utiliser --compare** pour mesurer l'impact réel du fine-tuning
3. **Le benchmark complet prend du temps** (~30-45 min) - réservez-le pour l'évaluation finale
4. **Sauvegarder les résultats** avec --output pour comparaisons futures
5. **Comparer avec reference_answers.md** pour une évaluation objective

---

## 🚀 Quick Start

```bash
# Test le plus simple
python test.py --model Apertus-FT/output/apertus_lora_custom_001 --question "Bonjour!"

# Test le plus complet
python test.py --model Apertus-FT/output/apertus_lora_custom_001 --compare --benchmark
```

C'est tout! Un seul script, toutes les fonctionnalités. 🎯
