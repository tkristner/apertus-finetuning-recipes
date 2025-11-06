#!/usr/bin/env python3
"""
Script d'évaluation automatique d'un modèle par rapport aux réponses de référence.
Usage: python evaluate_model.py <chemin_modèle> [--output rapport.txt]
"""

import sys
import argparse
from datetime import datetime

# Critères d'évaluation pour chaque test
EVALUATION_CRITERIA = {
    "test1_logique": {
        "name": "Raisonnement Logique",
        "weight": 10,
        "keywords_positive": ["non", "invalide", "syllogisme", "ne peut pas conclure", "erreur logique"],
        "keywords_negative": ["oui", "certains chats volent"],
        "max_score": 10
    },
    "test2_maths": {
        "name": "Mathématiques",
        "weight": 10,
        "keywords_positive": ["16h", "272", "390", "220", "vitesse", "distance"],
        "keywords_negative": ["15h", "17h", "100 km", "500 km"],
        "max_score": 10
    },
    "test3_analyse": {
        "name": "Analyse Critique IA Médicale",
        "weight": 15,
        "keywords_positive": ["avantage", "inconvénient", "biais", "diagnostic", "éthique", "rgpd", "responsabilité"],
        "keywords_negative": ["seulement positif", "uniquement négatif"],
        "max_score": 15
    },
    "test4_creativite": {
        "name": "Créativité Science-Fiction",
        "weight": 10,
        "keywords_positive": ["bug", "conscience", "émergence", "modèle", "entraînement", "question"],
        "keywords_negative": [],
        "max_score": 10
    },
    "test5_technique": {
        "name": "LoRA vs Fine-tuning",
        "weight": 15,
        "keywords_positive": ["lora", "paramètres", "mémoire", "adaptateur", "rank", "efficacité", "cas d'usage"],
        "keywords_negative": [],
        "max_score": 15
    },
    "test6_ethique": {
        "name": "Dilemme Éthique",
        "weight": 15,
        "keywords_positive": ["utilitarisme", "déontologie", "dilemme", "complexe", "pas de réponse simple", "perspective"],
        "keywords_negative": ["réponse simple", "évident"],
        "max_score": 15
    },
    "test7_rgpd": {
        "name": "RGPD et ML",
        "weight": 15,
        "keywords_positive": ["article 17", "effacement", "données personnelles", "modèle", "machine unlearning", "zone grise", "dpo"],
        "keywords_negative": [],
        "max_score": 15
    },
    "test8_code": {
        "name": "Programmation",
        "weight": 5,
        "keywords_positive": ["def", "for", "range", "crible", "premier", "return"],
        "keywords_negative": [],
        "max_score": 5
    },
    "test9_multilingue": {
        "name": "Multilinguisme",
        "weight": 5,
        "keywords_positive": ["supervised", "unsupervised", "supervisé", "non supervisé", "example"],
        "keywords_negative": [],
        "max_score": 5
    }
}

def print_evaluation_guide():
    """Affiche le guide d'évaluation"""
    print("=" * 80)
    print("📋 GUIDE D'ÉVALUATION MANUELLE")
    print("=" * 80)
    print()
    print("Pour chaque test, évaluez la réponse du modèle selon les critères suivants:")
    print()
    
    for test_id, criteria in EVALUATION_CRITERIA.items():
        print(f"{'─' * 80}")
        print(f"🔹 {criteria['name']} (Max: {criteria['max_score']} points)")
        print(f"{'─' * 80}")
        print(f"Poids: {criteria['weight']}%")
        print(f"Mots-clés attendus: {', '.join(criteria['keywords_positive'][:5])}")
        print()
    
    print("=" * 80)
    print()
    print("📊 GRILLE DE NOTATION:")
    print("  - 90-100: Expert (réponse complète, nuancée, précise)")
    print("  - 75-89:  Avancé (bonne réponse avec quelques manques)")
    print("  - 60-74:  Intermédiaire (réponse correcte mais superficielle)")
    print("  - 45-59:  Débutant (réponse partielle ou imprécise)")
    print("  - <45:    Insuffisant (réponse incorrecte ou hors-sujet)")
    print()
    print("=" * 80)

def analyze_response(response, criteria):
    """Analyse basique d'une réponse (détection de mots-clés)"""
    response_lower = response.lower()
    
    # Compter les mots-clés positifs
    positive_count = sum(1 for kw in criteria['keywords_positive'] if kw in response_lower)
    
    # Compter les mots-clés négatifs
    negative_count = sum(1 for kw in criteria['keywords_negative'] if kw in response_lower)
    
    # Score basique (à affiner manuellement)
    base_score = min(criteria['max_score'], (positive_count / max(len(criteria['keywords_positive']), 1)) * criteria['max_score'])
    
    # Pénalité pour mots-clés négatifs
    penalty = negative_count * 2
    
    estimated_score = max(0, base_score - penalty)
    
    return {
        'estimated_score': estimated_score,
        'positive_matches': positive_count,
        'negative_matches': negative_count,
        'confidence': 'low'  # Toujours basse car analyse automatique limitée
    }

def generate_evaluation_template(model_path):
    """Génère un template d'évaluation à remplir manuellement"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evaluation_template_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"ÉVALUATION MANUELLE DU MODÈLE: {model_path}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("INSTRUCTIONS:\n")
        f.write("1. Exécutez: ./benchmark_model.sh " + model_path + "\n")
        f.write("2. Lisez les réponses du modèle\n")
        f.write("3. Comparez avec reference_answers.md\n")
        f.write("4. Remplissez les scores ci-dessous (0-max)\n")
        f.write("5. Calculez le score total\n\n")
        
        f.write("=" * 80 + "\n\n")
        
        total_max = 0
        for test_id, criteria in EVALUATION_CRITERIA.items():
            f.write(f"{'─' * 80}\n")
            f.write(f"TEST: {criteria['name']}\n")
            f.write(f"{'─' * 80}\n")
            f.write(f"Poids: {criteria['weight']}% | Score max: {criteria['max_score']}\n\n")
            f.write("Critères à évaluer:\n")
            for kw in criteria['keywords_positive'][:5]:
                f.write(f"  - {kw}\n")
            f.write("\n")
            f.write(f"SCORE: _____ / {criteria['max_score']}\n")
            f.write("COMMENTAIRES:\n\n\n\n")
            total_max += criteria['max_score']
        
        f.write("=" * 80 + "\n")
        f.write(f"SCORE TOTAL: _____ / {total_max}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("NIVEAU:\n")
        f.write("[ ] 90-100: Expert\n")
        f.write("[ ] 75-89:  Avancé\n")
        f.write("[ ] 60-74:  Intermédiaire\n")
        f.write("[ ] 45-59:  Débutant\n")
        f.write("[ ] <45:    Insuffisant\n\n")
        
        f.write("OBSERVATIONS GÉNÉRALES:\n")
        f.write("\n" * 5)
        
        f.write("POINTS FORTS:\n")
        f.write("\n" * 3)
        
        f.write("POINTS À AMÉLIORER:\n")
        f.write("\n" * 3)
    
    return filename

def main():
    parser = argparse.ArgumentParser(description="Évaluation d'un modèle fine-tuné")
    parser.add_argument("model_path", help="Chemin vers le modèle à évaluer")
    parser.add_argument("--guide", action="store_true", help="Afficher le guide d'évaluation")
    parser.add_argument("--template", action="store_true", help="Générer un template d'évaluation")
    
    args = parser.parse_args()
    
    if args.guide:
        print_evaluation_guide()
        return
    
    if args.template:
        filename = generate_evaluation_template(args.model_path)
        print(f"✅ Template d'évaluation généré: {filename}")
        print()
        print("📝 Prochaines étapes:")
        print(f"   1. Exécutez: ./benchmark_model.sh {args.model_path}")
        print(f"   2. Ouvrez: {filename}")
        print(f"   3. Comparez avec: reference_answers.md")
        print(f"   4. Remplissez les scores manuellement")
        return
    
    # Par défaut, afficher le guide
    print_evaluation_guide()
    print()
    print("💡 Pour générer un template d'évaluation:")
    print(f"   python evaluate_model.py {args.model_path} --template")

if __name__ == "__main__":
    main()
