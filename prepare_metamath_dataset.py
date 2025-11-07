#!/usr/bin/env python3
"""
Prépare un sous-ensemble du dataset MetaMathQA pour le fine-tuning
MetaMathQA contient des problèmes mathématiques avec raisonnement étape par étape
"""

import json
from datasets import load_dataset
from pathlib import Path
import random

def prepare_metamath_subset(output_dir="./data/metamath_subset", sample_ratio=0.2, max_samples=10000):
    """
    Charge MetaMathQA et extrait un sous-ensemble pour le fine-tuning
    
    Args:
        output_dir: Répertoire de sortie
        sample_ratio: Ratio d'échantillonnage (0.2 = 20%)
        max_samples: Nombre maximum d'exemples
    """
    print("🔄 Chargement du dataset MetaMathQA...")
    
    # Charger MetaMathQA depuis HuggingFace
    # Note: MetaMathQA est un dataset de 395K exemples
    try:
        dataset = load_dataset("meta-math/MetaMathQA", split="train")
        print(f"✅ Dataset chargé: {len(dataset)} exemples")
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        print("💡 Tentative avec un autre nom...")
        dataset = load_dataset("meta-math/MetaMathQA-395K", split="train")
        print(f"✅ Dataset chargé: {len(dataset)} exemples")
    
    # Calculer le nombre d'exemples à échantillonner
    num_samples = min(int(len(dataset) * sample_ratio), max_samples)
    print(f"📊 Échantillonnage de {num_samples} exemples ({sample_ratio*100}%)")
    
    # Échantillonner aléatoirement
    indices = random.sample(range(len(dataset)), num_samples)
    sampled_dataset = dataset.select(indices)
    
    # Convertir au format attendu
    print("🔄 Conversion au format de fine-tuning...")
    converted_examples = []
    
    for idx, example in enumerate(sampled_dataset):
        if idx % 1000 == 0:
            print(f"   Traité: {idx}/{num_samples}")
        
        # MetaMathQA a les champs: query, response, type, original_question
        question = example.get("query", "")
        answer = example.get("response", "")
        
        if not question or not answer:
            continue
        
        # Format pour le fine-tuning avec système prompt
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant specialized in mathematics and logical reasoning. Provide step-by-step solutions."
            },
            {
                "role": "user",
                "content": question
            },
            {
                "role": "assistant",
                "content": answer
            }
        ]
        
        converted_examples.append({
            "messages": messages,
            "source": "MetaMathQA",
            "type": example.get("type", "unknown")
        })
    
    print(f"✅ Converti {len(converted_examples)} exemples")
    
    # Créer le répertoire de sortie
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder en JSONL
    output_file = output_path / "train.jsonl"
    print(f"💾 Sauvegarde dans {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in converted_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Dataset sauvegardé: {output_file}")
    
    # Statistiques
    print("\n📊 Statistiques:")
    print(f"   - Total exemples: {len(converted_examples)}")
    print(f"   - Source: MetaMathQA")
    print(f"   - Format: Chat avec système prompt")
    
    # Types de problèmes
    types = {}
    for ex in converted_examples:
        t = ex.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
    
    print("\n📈 Répartition par type:")
    for t, count in sorted(types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {t}: {count} ({count/len(converted_examples)*100:.1f}%)")
    
    # Exemple
    print("\n📝 Exemple:")
    if converted_examples:
        ex = converted_examples[0]
        print(f"   Question: {ex['messages'][1]['content'][:100]}...")
        print(f"   Réponse: {ex['messages'][2]['content'][:100]}...")
    
    return output_file

def create_combined_dataset(metamath_path, custom_path, output_path="./data/combined_dataset", metamath_ratio=0.2):
    """
    Combine MetaMathQA avec votre dataset personnalisé
    
    Args:
        metamath_path: Chemin vers le fichier MetaMathQA
        custom_path: Chemin vers le dataset personnalisé
        output_path: Répertoire de sortie
        metamath_ratio: Ratio de MetaMathQA dans le dataset final (0.2 = 20%)
    """
    print("\n🔄 Création du dataset combiné...")
    print(f"📊 Ratio cible: {(1-metamath_ratio)*100:.0f}% Custom / {metamath_ratio*100:.0f}% MetaMathQA")
    
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Charger dataset personnalisé (prioritaire)
    print(f"\n📂 Chargement du dataset personnalisé...")
    custom_examples = []
    
    # Détecter si c'est un fichier ou un dossier
    custom_path_obj = Path(custom_path)
    
    if custom_path_obj.is_file():
        # C'est un fichier direct (ex: all_DPO_sources_0.95-dedup.jsonl)
        custom_file = custom_path_obj
    else:
        # C'est un dossier, chercher train.jsonl dedans
        custom_file = custom_path_obj / "train.jsonl"
    
    if custom_file.exists():
        print(f"   📄 Lecture de {custom_file}...")
        with open(custom_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                data['source'] = 'custom'
                custom_examples.append(data)
        print(f"   ✅ {len(custom_examples)} exemples personnalisés chargés")
    else:
        print(f"   ⚠️ Fichier non trouvé: {custom_file}")
        print(f"   ⚠️ Création du dataset avec MetaMathQA uniquement")
        custom_examples = []
    
    # Charger MetaMathQA
    print(f"\n📂 Chargement de MetaMathQA...")
    metamath_examples = []
    with open(metamath_path, 'r', encoding='utf-8') as f:
        for line in f:
            metamath_examples.append(json.loads(line))
    print(f"   ✅ {len(metamath_examples)} exemples MetaMathQA disponibles")
    
    # Calculer le nombre d'exemples MetaMathQA nécessaires
    if len(custom_examples) > 0:
        # Formule: custom / (custom + metamath) = (1 - ratio)
        # => metamath = custom * ratio / (1 - ratio)
        target_metamath = int(len(custom_examples) * metamath_ratio / (1 - metamath_ratio))
        target_metamath = min(target_metamath, len(metamath_examples))
    else:
        # Si pas de custom, prendre tous les MetaMathQA
        target_metamath = len(metamath_examples)
    
    print(f"\n🎯 Calcul des proportions:")
    print(f"   - Custom: {len(custom_examples)} exemples (cible: {(1-metamath_ratio)*100:.0f}%)")
    print(f"   - MetaMathQA: {target_metamath} exemples (cible: {metamath_ratio*100:.0f}%)")
    
    # Échantillonner MetaMathQA si nécessaire
    if target_metamath < len(metamath_examples):
        print(f"   🔀 Échantillonnage de {target_metamath} exemples MetaMathQA...")
        metamath_examples = random.sample(metamath_examples, target_metamath)
    
    # Combiner
    combined = custom_examples + metamath_examples
    
    # Mélanger
    print("\n🔀 Mélange du dataset...")
    random.shuffle(combined)
    
    # Sauvegarder
    output_file = output_dir / "train.jsonl"
    print(f"💾 Sauvegarde dans {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in combined:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    # Statistiques finales
    actual_custom_ratio = len(custom_examples) / len(combined) if len(combined) > 0 else 0
    actual_metamath_ratio = len(metamath_examples) / len(combined) if len(combined) > 0 else 0
    
    print(f"\n✅ Dataset combiné créé: {output_file}")
    print(f"\n📊 STATISTIQUES FINALES:")
    print(f"   - Total: {len(combined)} exemples")
    print(f"   - Custom (Data Protection): {len(custom_examples)} ({actual_custom_ratio*100:.1f}%)")
    print(f"   - MetaMathQA: {len(metamath_examples)} ({actual_metamath_ratio*100:.1f}%)")
    
    return output_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Prépare un sous-ensemble de MetaMathQA")
    parser.add_argument("--ratio", type=float, default=0.2, help="Ratio d'échantillonnage initial de MetaMathQA (défaut: 0.2 = 20%%)")
    parser.add_argument("--max-samples", type=int, default=10000, help="Nombre max d'exemples MetaMathQA (défaut: 10000)")
    parser.add_argument("--output", type=str, default="./data/metamath_subset", help="Répertoire de sortie")
    parser.add_argument("--combine", action="store_true", help="Combiner avec le dataset personnalisé")
    parser.add_argument("--custom-path", type=str, default="./data/converted_dataset", help="Chemin du dataset personnalisé")
    parser.add_argument("--metamath-ratio", type=float, default=0.2, help="Ratio de MetaMathQA dans le dataset final (défaut: 0.2 = 20%%, donc 80%% custom)")
    
    args = parser.parse_args()
    
    # Préparer MetaMathQA
    metamath_file = prepare_metamath_subset(
        output_dir=args.output,
        sample_ratio=args.ratio,
        max_samples=args.max_samples
    )
    
    # Combiner si demandé
    if args.combine:
        combined_file = create_combined_dataset(
            metamath_path=metamath_file,
            custom_path=args.custom_path,
            output_path="./data/combined_dataset",
            metamath_ratio=args.metamath_ratio
        )
        print(f"\n🎉 Dataset combiné prêt: {combined_file}")
        print(f"📝 Pour l'utiliser, modifiez sft_lora_custom.yaml:")
        print(f"   dataset_name: ./data/combined_dataset")
    else:
        print(f"\n🎉 Dataset MetaMathQA prêt: {metamath_file}")
        print(f"📝 Pour combiner avec votre dataset:")
        print(f"   python prepare_metamath_dataset.py --combine")
