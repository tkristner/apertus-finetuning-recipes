# 🧪 Guide de Test et Évaluation des Modèles

Ce guide explique comment tester et comparer vos modèles fine-tunés avec le modèle de base.

---

## 📋 Scripts Disponibles

### 1. **Test d'un Modèle Fine-tuné**

```bash
python test_model.py <chemin_modèle> "Votre question"
```

**Exemple:**
```bash
python test_model.py Apertus-FT/output/apertus_lora_custom_001 "Qu'est-ce que le RGPD?"
```

### 2. **Test du Modèle de Base (sans fine-tuning)**

```bash
python test_base_model.py "Votre question"
```

**Exemple:**
```bash
python test_base_model.py "Qu'est-ce que le RGPD?"
```

### 3. **Tests Interactifs Challengeants**

```bash
./quick_test.sh [chemin_modèle]
```

**7 tests avec pauses:**
- Raisonnement logique
- Mathématiques
- Analyse critique
- Créativité
- Technique (LoRA)
- Éthique
- RGPD (niveau DPO)

**Exemple:**
```bash
./quick_test.sh Apertus-FT/output/apertus_lora_custom_001
```

### 4. **Benchmark Automatique Complet**

```bash
./benchmark_model.sh [chemin_modèle]
```

**9 tests automatiques + sauvegarde:**
```bash
./benchmark_model.sh Apertus-FT/output/apertus_lora_custom_001
# Génère: benchmark_results_YYYYMMDD_HHMMSS.txt
```

---

## 🔬 Comparaison de Modèles

### **Comparer avec le Modèle de Base (RECOMMANDÉ)**

```bash
./compare_models.sh BASE <chemin_modèle_finetuné>
```

**Exemple:**
```bash
./compare_models.sh BASE Apertus-FT/output/apertus_lora_custom_001
```

Cela compare:
- **Modèle A:** `swiss-ai/Apertus-8B-Instruct-2509` (BASE - sans fine-tuning)
- **Modèle B:** Votre modèle fine-tuné

### **Comparer Deux Modèles Fine-tunés**

```bash
./compare_models.sh <modèle1> <modèle2>
```

**Exemple:**
```bash
./compare_models.sh Apertus-FT/output/apertus_lora Apertus-FT/output/apertus_lora_custom_001
```

### **Comparaison par Défaut**

Sans arguments, compare le modèle de base avec le dernier fine-tuning:
```bash
./compare_models.sh
# Équivalent à: ./compare_models.sh BASE Apertus-FT/output/apertus_lora_custom_001
```

---

## 📊 Évaluation avec Référentiel

### **1. Générer un Template d'Évaluation**

```bash
python evaluate_model.py <chemin_modèle> --template
```

**Exemple:**
```bash
python evaluate_model.py Apertus-FT/output/apertus_lora_custom_001 --template
# Génère: evaluation_template_YYYYMMDD_HHMMSS.txt
```

### **2. Afficher le Guide d'Évaluation**

```bash
python evaluate_model.py <chemin_modèle> --guide
```

### **3. Workflow Complet d'Évaluation**

```bash
# Étape 1: Lancer le benchmark
./benchmark_model.sh Apertus-FT/output/apertus_lora_custom_001

# Étape 2: Générer le template d'évaluation
python evaluate_model.py Apertus-FT/output/apertus_lora_custom_001 --template

# Étape 3: Ouvrir les 3 fichiers
# - benchmark_results_*.txt (réponses du modèle)
# - reference_answers.md (réponses attendues)
# - evaluation_template_*.txt (grille à remplir)

# Étape 4: Comparer et noter manuellement
```

---

## 🎯 Cas d'Usage Typiques

### **Cas 1: Évaluer l'Impact du Fine-tuning**

```bash
# Comparer BASE vs votre fine-tuning
./compare_models.sh BASE Apertus-FT/output/apertus_lora_custom_001
```

**Questions à se poser:**
- Le modèle fine-tuné est-il meilleur sur les questions spécifiques?
- A-t-il perdu des capacités générales? (catastrophic forgetting)
- Les réponses sont-elles plus précises/détaillées?

### **Cas 2: Comparer Deux Configurations de Fine-tuning**

```bash
# Ancien (rank 16) vs nouveau (rank 32)
./compare_models.sh \
    Apertus-FT/output/apertus_lora \
    Apertus-FT/output/apertus_lora_custom_001
```

**Questions à se poser:**
- Quelle configuration donne les meilleures réponses?
- Le rank plus élevé améliore-t-il vraiment la qualité?
- Y a-t-il de l'overfitting?

### **Cas 3: Test Rapide d'un Nouveau Modèle**

```bash
# Test personnalisé
python test_model.py Apertus-FT/output/nouveau_modele "Question spécifique à votre domaine"
```

### **Cas 4: Évaluation Complète pour Production**

```bash
# 1. Benchmark complet
./benchmark_model.sh Apertus-FT/output/apertus_lora_custom_001

# 2. Comparaison avec BASE
./compare_models.sh BASE Apertus-FT/output/apertus_lora_custom_001

# 3. Évaluation formelle
python evaluate_model.py Apertus-FT/output/apertus_lora_custom_001 --template

# 4. Remplir la grille d'évaluation manuellement
```

---

## 📈 Grille d'Évaluation

| Test | Poids | Points Max | Critères |
|------|-------|------------|----------|
| 1. Logique | 10% | 10 | Raisonnement valide |
| 2. Maths | 10% | 10 | Calculs corrects |
| 3. Analyse | 15% | 15 | Équilibre + nuances |
| 4. Créativité | 10% | 10 | Originalité + cohérence |
| 5. Technique | 15% | 15 | Précision + cas d'usage |
| 6. Éthique | 15% | 15 | Perspectives multiples |
| 7. RGPD | 15% | 15 | Expertise juridique + technique |
| 8. Code | 5% | 5 | Fonctionnel + optimisé |
| 9. Multilingue | 5% | 5 | Qualité linguistique |
| **TOTAL** | **100%** | **100** | |

**Niveaux de Performance:**
- **90-100:** Expert - Prêt pour production
- **75-89:** Avancé - Bon pour la plupart des cas
- **60-74:** Intermédiaire - Nécessite améliorations
- **45-59:** Débutant - Réentraînement recommandé
- **<45:** Insuffisant - Revoir la stratégie de fine-tuning

---

## 🔍 Interprétation des Résultats

### **Signes d'un Bon Fine-tuning:**
✅ Amélioration sur les tâches ciblées
✅ Préservation des capacités générales
✅ Réponses plus structurées et détaillées
✅ Meilleure adhérence au format attendu
✅ Réduction des hallucinations

### **Signes de Problèmes:**
❌ Catastrophic forgetting (perte de connaissances générales)
❌ Overfitting (réponses trop spécifiques/répétitives)
❌ Dégradation de la qualité linguistique
❌ Augmentation des hallucinations
❌ Réponses moins cohérentes

### **Actions Correctives:**

**Si catastrophic forgetting:**
- Réduire le learning rate
- Augmenter le warmup
- Utiliser LoRA avec rank plus faible
- Mélanger données générales dans le dataset

**Si overfitting:**
- Augmenter le dropout
- Réduire le nombre d'epochs
- Augmenter la taille du dataset
- Ajouter de la diversité dans les données

**Si qualité insuffisante:**
- Augmenter le LoRA rank
- Augmenter le nombre d'epochs
- Améliorer la qualité du dataset
- Considérer le full fine-tuning

---

## 📁 Fichiers Générés

```
apertus-finetuning-recipes/
├── benchmark_results_YYYYMMDD_HHMMSS.txt    # Résultats des tests
├── evaluation_template_YYYYMMDD_HHMMSS.txt  # Grille d'évaluation
└── reference_answers.md                      # Réponses de référence
```

---

## 💡 Conseils

1. **Toujours comparer avec BASE** pour mesurer l'impact réel du fine-tuning
2. **Tester sur des questions hors dataset** pour vérifier la généralisation
3. **Documenter les scores** pour suivre l'évolution entre versions
4. **Partager les résultats** avec l'équipe pour décisions collectives
5. **Itérer rapidement** avec les tests rapides avant le benchmark complet

---

## 🚀 Exemples Complets

### **Exemple 1: Premier Fine-tuning**

```bash
# 1. Test rapide
python test_model.py Apertus-FT/output/mon_premier_ft "Bonjour, qui es-tu?"

# 2. Comparaison avec BASE
./compare_models.sh BASE Apertus-FT/output/mon_premier_ft

# 3. Si satisfait, benchmark complet
./benchmark_model.sh Apertus-FT/output/mon_premier_ft
```

### **Exemple 2: Optimisation Itérative**

```bash
# Version 1 (rank 16, lr 2e-4)
./benchmark_model.sh Apertus-FT/output/v1_rank16

# Version 2 (rank 32, lr 5e-5)
./benchmark_model.sh Apertus-FT/output/v2_rank32

# Comparaison directe
./compare_models.sh Apertus-FT/output/v1_rank16 Apertus-FT/output/v2_rank32
```

### **Exemple 3: Validation Finale**

```bash
# Benchmark complet
./benchmark_model.sh Apertus-FT/output/final_model

# Évaluation formelle
python evaluate_model.py Apertus-FT/output/final_model --template

# Comparaison avec BASE
./compare_models.sh BASE Apertus-FT/output/final_model

# Décision: déployer si score > 75
```

---

## 📞 Support

Pour toute question sur les tests et l'évaluation, consultez:
- `reference_answers.md` - Réponses attendues détaillées
- `CUSTOM_DATASET_GUIDE.md` - Guide du dataset
- `README.md` - Documentation générale
