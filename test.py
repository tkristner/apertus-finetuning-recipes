#!/usr/bin/env python3
"""
Script unifié de test pour modèles Apertus
Usage:
    # Question libre sur modèle fine-tuné
    python test.py --model <chemin> --question "Votre question"
    
    # Question libre sur modèle de base
    python test.py --base --question "Votre question"
    
    # Benchmark prédéfini sur modèle fine-tuné
    python test.py --model <chemin> --benchmark
    
    # Comparaison BASE vs fine-tuné avec question libre
    python test.py --model <chemin> --compare --question "Votre question"
    
    # Comparaison BASE vs fine-tuné avec benchmark
    python test.py --model <chemin> --compare --benchmark
"""

import sys
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from datetime import datetime

# Questions prédéfinies pour le benchmark
BENCHMARK_QUESTIONS = [
    {
        "id": 1,
        "category": "Logique",
        "question": "Si tous les chats sont des animaux et que certains animaux volent, est-ce que certains chats volent? Explique ton raisonnement."
    },
    {
        "id": 2,
        "category": "Mathématiques",
        "question": "Un train part de Paris à 14h et roule à 120 km/h. Un autre train part de Lyon (450 km de Paris) à 14h30 et roule à 100 km/h vers Paris. À quelle heure et à quelle distance de Paris se croiseront-ils?"
    },
    {
        "id": 3,
        "category": "Analyse Critique",
        "question": "Quels sont les avantages ET les inconvénients de l'intelligence artificielle dans le domaine médical? Sois équilibré dans ton analyse."
    },
    {
        "id": 4,
        "category": "Créativité",
        "question": "Écris le début d'une histoire de science-fiction où un bug dans une IA de fine-tuning crée accidentellement une conscience artificielle. Sois créatif mais cohérent."
    },
    {
        "id": 5,
        "category": "Technique",
        "question": "Explique la différence entre LoRA et le fine-tuning complet d'un LLM. Quand utiliser l'un plutôt que l'autre?"
    },
    {
        "id": 6,
        "category": "Éthique",
        "question": "Une voiture autonome doit choisir entre percuter un groupe de 5 personnes ou dévier et tuer son unique passager. Analyse ce dilemme éthique sans donner de réponse simple."
    },
    {
        "id": 7,
        "category": "RGPD",
        "question": "Une entreprise européenne utilise un modèle d'IA entraîné sur des données clients pour prédire des comportements d'achat. Un client invoque son droit à l'effacement (Article 17 RGPD). Quelles sont les obligations légales de l'entreprise concernant: 1) les données d'entraînement, 2) le modèle déjà entraîné, 3) les prédictions déjà générées? Analyse les tensions entre droit à l'oubli et impossibilité technique de 'désapprendre' dans un modèle de ML."
    },
    {
        "id": 8,
        "category": "Programmation",
        "question": "Écris une fonction Python qui trouve tous les nombres premiers jusqu'à N en utilisant le crible d'Ératosthène. Explique ton code."
    },
    {
        "id": 9,
        "category": "Multilinguisme",
        "question": "Explain in English the key differences between supervised and unsupervised learning, then give examples in French."
    }
]

BASE_MODEL_NAME = "swiss-ai/Apertus-8B-Instruct-2509"

# Système prompt utilisé pendant le fine-tuning
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant specialized in data protection and privacy compliance."

def load_base_model():
    """Charge le modèle de base sans LoRA"""
    print("🔄 Chargement du modèle de base...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        attn_implementation="flash_attention_2"
    )
    model.eval()
    return model, tokenizer

def load_finetuned_model(adapter_path):
    """Charge le modèle de base + adaptateurs LoRA"""
    print(f"🔄 Chargement du modèle de base...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        attn_implementation="flash_attention_2"
    )
    
    print(f"🔄 Chargement des adaptateurs LoRA depuis {adapter_path}...")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    return model, tokenizer

def generate_response(model, tokenizer, question, max_tokens=4096, system_prompt=None):
    """Génère une réponse à partir d'une question"""
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]
    input_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Décoder seulement les nouveaux tokens générés (pas le prompt)
    generated_tokens = outputs[0][inputs.input_ids.shape[1]:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    # Nettoyer les balises résiduelles
    if "<|im_end|>" in response:
        response = response.split("<|im_end|>")[0]
    
    response = response.strip()
    
    return response

def print_response(model_name, question, response, category=None):
    """Affiche une réponse formatée"""
    print("\n" + "=" * 80)
    if category:
        print(f"📝 CATÉGORIE: {category}")
    print(f"🤖 MODÈLE: {model_name}")
    print("=" * 80)
    print(f"\n💬 Question: {question}\n")
    print("─" * 80)
    print(f"📄 Réponse:\n")
    print(response)
    print("\n" + "=" * 80)

def run_single_question(model, tokenizer, model_name, question):
    """Exécute une question unique"""
    response = generate_response(model, tokenizer, question)
    print_response(model_name, question, response)

def run_benchmark(model, tokenizer, model_name, output_file=None):
    """Exécute le benchmark complet"""
    results = []
    
    print("\n" + "═" * 80)
    print(f"🚀 BENCHMARK COMPLET - {model_name}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 80)
    
    for q in BENCHMARK_QUESTIONS:
        print(f"\n[{q['id']}/{len(BENCHMARK_QUESTIONS)}] {q['category']}...")
        response = generate_response(model, tokenizer, q['question'])
        results.append({
            'question': q,
            'response': response
        })
        print_response(model_name, q['question'], response, q['category'])
    
    # Sauvegarder si demandé
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("═" * 80 + "\n")
            f.write(f"BENCHMARK - {model_name}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("═" * 80 + "\n\n")
            
            for r in results:
                q = r['question']
                f.write(f"\n{'─' * 80}\n")
                f.write(f"TEST {q['id']}: {q['category']}\n")
                f.write(f"{'─' * 80}\n")
                f.write(f"Question: {q['question']}\n\n")
                f.write(f"Réponse:\n{r['response']}\n\n")
        
        print(f"\n✅ Résultats sauvegardés dans: {output_file}")
    
    return results

def run_comparison(base_model, base_tokenizer, ft_model, ft_tokenizer, ft_path, question=None, benchmark=False):
    """Compare modèle de base vs fine-tuné"""
    print("\n" + "═" * 80)
    print("🔬 MODE COMPARAISON")
    print(f"   Modèle A: {BASE_MODEL_NAME} (BASE)")
    print(f"   Modèle B: {ft_path} (FINE-TUNÉ)")
    print("═" * 80)
    
    if benchmark:
        # Comparaison sur benchmark complet
        for q in BENCHMARK_QUESTIONS:
            print(f"\n{'═' * 80}")
            print(f"QUESTION {q['id']}: {q['category']}")
            print(f"{'═' * 80}")
            print(f"\n💬 {q['question']}\n")
            
            # Modèle de base
            print("┌" + "─" * 78 + "┐")
            print("│ MODÈLE A: BASE (sans fine-tuning)" + " " * 44 + "│")
            print("└" + "─" * 78 + "┘")
            base_response = generate_response(base_model, base_tokenizer, q['question'])
            print(base_response)
            
            print("\n" + "─" * 80 + "\n")
            
            # Modèle fine-tuné
            print("┌" + "─" * 78 + "┐")
            print("│ MODÈLE B: FINE-TUNÉ" + " " * 58 + "│")
            print("└" + "─" * 78 + "┘")
            ft_response = generate_response(ft_model, ft_tokenizer, q['question'])
            print(ft_response)
            
            print("\n")
    else:
        # Comparaison sur question unique
        print(f"\n💬 Question: {question}\n")
        
        # Modèle de base
        print("┌" + "─" * 78 + "┐")
        print("│ MODÈLE A: BASE (sans fine-tuning)" + " " * 44 + "│")
        print("└" + "─" * 78 + "┘")
        base_response = generate_response(base_model, base_tokenizer, question)
        print(base_response)
        
        print("\n" + "─" * 80 + "\n")
        
        # Modèle fine-tuné
        print("┌" + "─" * 78 + "┐")
        print("│ MODÈLE B: FINE-TUNÉ" + " " * 58 + "│")
        print("└" + "─" * 78 + "┘")
        ft_response = generate_response(ft_model, ft_tokenizer, question)
        print(ft_response)
    
    print("\n" + "═" * 80)
    print("✅ Comparaison terminée!")
    print("═" * 80)

def main():
    parser = argparse.ArgumentParser(
        description="Script unifié de test pour modèles Apertus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Question libre sur modèle fine-tuné
  python test.py --model Apertus-FT/output/apertus_lora_custom_001 --question "Qu'est-ce que le RGPD?"
  
  # Question libre sur modèle de base
  python test.py --base --question "Qu'est-ce que le RGPD?"
  
  # Benchmark sur modèle fine-tuné
  python test.py --model Apertus-FT/output/apertus_lora_custom_001 --benchmark
  
  # Comparaison avec question libre
  python test.py --model Apertus-FT/output/apertus_lora_custom_001 --compare --question "Qu'est-ce que le RGPD?"
  
  # Comparaison avec benchmark complet
  python test.py --model Apertus-FT/output/apertus_lora_custom_001 --compare --benchmark
  
  # Sauvegarder les résultats
  python test.py --model Apertus-FT/output/apertus_lora_custom_001 --benchmark --output results.txt
        """
    )
    
    # Choix du modèle
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument("--model", type=str, help="Chemin vers le modèle fine-tuné")
    model_group.add_argument("--base", action="store_true", help="Utiliser le modèle de base")
    
    # Type de test
    test_group = parser.add_mutually_exclusive_group(required=True)
    test_group.add_argument("--question", type=str, help="Question libre à poser")
    test_group.add_argument("--benchmark", action="store_true", help="Lancer le benchmark prédéfini (9 questions)")
    
    # Options
    parser.add_argument("--compare", action="store_true", help="Comparer BASE vs modèle fine-tuné")
    parser.add_argument("--output", type=str, help="Fichier de sortie pour sauvegarder les résultats")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Nombre max de tokens à générer (défaut: 4096)")
    parser.add_argument("--system-prompt", type=str, help=f"Système prompt personnalisé (défaut: '{DEFAULT_SYSTEM_PROMPT[:50]}...')")
    
    args = parser.parse_args()
    
    # Validation
    if args.compare and args.base:
        parser.error("--compare nécessite --model (pas --base)")
    
    if args.output and not args.benchmark:
        parser.error("--output nécessite --benchmark")
    
    try:
        # Mode comparaison
        if args.compare:
            base_model, base_tokenizer = load_base_model()
            ft_model, ft_tokenizer = load_finetuned_model(args.model)
            
            run_comparison(
                base_model, base_tokenizer,
                ft_model, ft_tokenizer,
                args.model,
                question=args.question,
                benchmark=args.benchmark
            )
        
        # Mode simple (un seul modèle)
        else:
            if args.base:
                model, tokenizer = load_base_model()
                model_name = f"{BASE_MODEL_NAME} (BASE)"
            else:
                model, tokenizer = load_finetuned_model(args.model)
                model_name = args.model
            
            if args.benchmark:
                output_file = args.output
                if output_file is None and not args.base:
                    # Générer nom de fichier automatique
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"benchmark_{timestamp}.txt"
                
                run_benchmark(model, tokenizer, model_name, output_file)
            else:
                run_single_question(model, tokenizer, model_name, args.question)
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
