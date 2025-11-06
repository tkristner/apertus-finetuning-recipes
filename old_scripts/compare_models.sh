#!/bin/bash
# Compare deux modèles sur les mêmes questions
# Supporte: modèle de base (BASE) ou modèles fine-tunés (chemin)

MODEL1="${1:-BASE}"
MODEL2="${2:-Apertus-FT/output/apertus_lora_custom_001}"

echo "🔬 Comparaison de modèles"
if [ "$MODEL1" = "BASE" ]; then
    echo "   Modèle A: swiss-ai/Apertus-8B-Instruct-2509 (BASE - sans fine-tuning)"
else
    echo "   Modèle A: $MODEL1"
fi
echo "   Modèle B: $MODEL2"
echo ""

# Questions de test
QUESTIONS=(
    "Explique en 3 phrases ce qu'est le fine-tuning."
    "Si j'ai 10 pommes et que j'en donne 3, combien m'en reste-t-il? Explique."
    "Quels sont les principaux défis de l'IA aujourd'hui?"
    "Écris un haiku sur l'intelligence artificielle."
)

for i in "${!QUESTIONS[@]}"; do
    QUESTION="${QUESTIONS[$i]}"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "QUESTION $((i+1)): $QUESTION"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Modèle A
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    if [ "$MODEL1" = "BASE" ]; then
        echo "│ MODÈLE A: Apertus-8B-Instruct-2509 (BASE)"
    else
        echo "│ MODÈLE A: $(basename $MODEL1)"
    fi
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    
    if [ "$MODEL1" = "BASE" ]; then
        python test_base_model.py "$QUESTION" 2>/dev/null | grep -A 100 "🤖 Réponse du modèle:" | grep -B 100 "^════" | head -n -1
    else
        python test_model.py "$MODEL1" "$QUESTION" 2>/dev/null | grep -A 100 "🤖 Réponse du modèle:" | grep -B 100 "^════" | head -n -1
    fi
    echo ""
    
    # Modèle B
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│ MODÈLE B: $(basename $MODEL2)"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    python test_model.py "$MODEL2" "$QUESTION" 2>/dev/null | grep -A 100 "🤖 Réponse du modèle:" | grep -B 100 "^════" | head -n -1
    echo ""
    echo ""
done

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ Comparaison terminée!"
echo "═══════════════════════════════════════════════════════════════════════════════"
