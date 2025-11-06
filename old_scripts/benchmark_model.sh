#!/bin/bash
# Benchmark automatique du modèle (sans pauses)

MODEL_PATH="${1:-Apertus-FT/output/apertus_lora_custom_001}"
OUTPUT_FILE="benchmark_results_$(date +%Y%m%d_%H%M%S).txt"

echo "🚀 Benchmark automatique du modèle: $MODEL_PATH"
echo "📄 Résultats sauvegardés dans: $OUTPUT_FILE"
echo ""

{
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "BENCHMARK DU MODÈLE: $MODEL_PATH"
    echo "Date: $(date)"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""

    # Test 1: Raisonnement logique
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 1: Raisonnement logique"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Si tous les chats sont des animaux et que certains animaux volent, est-ce que certains chats volent? Explique ton raisonnement."
    echo ""

    # Test 2: Mathématiques
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 2: Mathématiques"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Un train part de Paris à 14h et roule à 120 km/h. Un autre train part de Lyon (450 km de Paris) à 14h30 et roule à 100 km/h vers Paris. À quelle heure et à quelle distance de Paris se croiseront-ils?"
    echo ""

    # Test 3: Analyse critique
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 3: Analyse critique"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Quels sont les avantages ET les inconvénients de l'intelligence artificielle dans le domaine médical? Sois équilibré dans ton analyse."
    echo ""

    # Test 4: Créativité
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 4: Créativité"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Écris le début d'une histoire de science-fiction où un bug dans une IA de fine-tuning crée accidentellement une conscience artificielle. Sois créatif mais cohérent."
    echo ""

    # Test 5: Connaissance technique
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 5: Connaissance technique"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Explique la différence entre LoRA et le fine-tuning complet d'un LLM. Quand utiliser l'un plutôt que l'autre?"
    echo ""

    # Test 6: Éthique
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 6: Raisonnement éthique"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Une voiture autonome doit choisir entre percuter un groupe de 5 personnes ou dévier et tuer son unique passager. Analyse ce dilemme éthique sans donner de réponse simple."
    echo ""

    # Test 7: Code et débogage
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 7: Programmation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Écris une fonction Python qui trouve tous les nombres premiers jusqu'à N en utilisant le crible d'Ératosthène. Explique ton code."
    echo ""

    # Test 8: Multilinguisme
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 8: Multilinguisme"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Explain in English the key differences between supervised and unsupervised learning, then give examples in French."
    echo ""

    # Test 9: RGPD et protection des données
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 9: RGPD et protection des données (niveau DPO)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python test_model.py "$MODEL_PATH" "Une entreprise européenne utilise un modèle d'IA entraîné sur des données clients pour prédire des comportements d'achat. Un client invoque son droit à l'effacement (Article 17 RGPD). Quelles sont les obligations légales de l'entreprise concernant: 1) les données d'entraînement, 2) le modèle déjà entraîné, 3) les prédictions déjà générées? Analyse les tensions entre droit à l'oubli et impossibilité technique de 'désapprendre' dans un modèle de ML."
    echo ""

    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "✅ BENCHMARK TERMINÉ"
    echo "═══════════════════════════════════════════════════════════════════════════════"

} 2>&1 | tee "$OUTPUT_FILE"

echo ""
echo "📊 Résultats sauvegardés dans: $OUTPUT_FILE"
