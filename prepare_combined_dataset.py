#!/usr/bin/env python3
"""
Convertit le dataset combiné (JSONL) au format HuggingFace avec train/test split
"""
import json
from datasets import Dataset, DatasetDict
from pathlib import Path


def load_and_convert_combined_dataset(jsonl_path, train_split=0.9):
    """
    Charge le dataset combiné JSONL et le convertit au format HuggingFace
    
    Le dataset combiné a déjà le format messages correct:
    {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "source": "custom" ou "MetaMathQA"
    }
    
    Args:
        jsonl_path: Chemin vers le fichier JSONL combiné
        train_split: Proportion pour le training (défaut: 0.9 = 90%)
    
    Returns:
        DatasetDict avec splits train et test
    """
    print(f"📂 Chargement de {jsonl_path}...")
    
    # Charger le JSONL et convertir au format messages si nécessaire
    data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                
                # Si déjà au format messages, le garder
                if 'messages' in item:
                    data.append({'messages': item['messages']})
                # Sinon, convertir depuis le format question/answers (dataset custom)
                elif 'question' in item and 'answers' in item:
                    # Trouver la réponse choisie
                    chosen_answer = None
                    for answer in item['answers']:
                        if answer.get('type') == 'chosen' or answer.get('score', 0) >= 1.0:
                            chosen_answer = answer
                            break
                    
                    if not chosen_answer:
                        chosen_answer = item['answers'][0]
                    
                    # Créer le format messages
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful AI assistant specialized in data protection and privacy compliance."
                        },
                        {
                            "role": "user",
                            "content": item['question']
                        },
                        {
                            "role": "assistant",
                            "content": chosen_answer['text']
                        }
                    ]
                    data.append({'messages': messages})
    
    print(f"✅ Chargé {len(data)} exemples")
    
    # Compter les sources
    sources = {}
    for item in data:
        source = item.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📊 Répartition par source:")
    for source, count in sources.items():
        print(f"   - {source}: {count} ({count/len(data)*100:.1f}%)")
    
    # Créer le dataset HuggingFace
    print(f"\n🔄 Conversion au format HuggingFace...")
    dataset = Dataset.from_list(data)
    
    # Split train/test
    print(f"✂️  Split train/test ({train_split*100:.0f}% / {(1-train_split)*100:.0f}%)...")
    split_dataset = dataset.train_test_split(
        test_size=1 - train_split,
        seed=42,
        shuffle=True
    )
    
    dataset_dict = DatasetDict({
        "train": split_dataset["train"],
        "test": split_dataset["test"]
    })
    
    print(f"\n✅ Dataset créé:")
    print(f"   - Train: {len(dataset_dict['train'])} exemples")
    print(f"   - Test: {len(dataset_dict['test'])} exemples")
    
    return dataset_dict


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Convertit le dataset combiné au format HuggingFace")
    parser.add_argument("--input", type=str, default="./data/combined_dataset/train.jsonl", 
                       help="Chemin vers le fichier JSONL combiné")
    parser.add_argument("--output", type=str, default="./data/combined_dataset_hf",
                       help="Répertoire de sortie pour le dataset HuggingFace")
    parser.add_argument("--train-split", type=float, default=0.9,
                       help="Proportion pour le training (défaut: 0.9)")
    
    args = parser.parse_args()
    
    # Convertir
    dataset = load_and_convert_combined_dataset(args.input, args.train_split)
    
    # Sauvegarder
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Sauvegarde dans {output_dir}...")
    dataset.save_to_disk(str(output_dir))
    
    print(f"\n🎉 Dataset HuggingFace créé: {output_dir}")
    print(f"\n📝 Pour l'utiliser, modifiez votre config YAML:")
    print(f"   dataset_name: {output_dir}")
    
    # Afficher un exemple
    print(f"\n📋 Exemple (train):")
    example = dataset['train'][0]
    print(f"   Source: {example.get('source', 'N/A')}")
    print(f"   Messages: {len(example['messages'])} messages")
    print(f"   System: {example['messages'][0]['content'][:80]}...")
    print(f"   User: {example['messages'][1]['content'][:80]}...")
    print(f"   Assistant: {example['messages'][2]['content'][:80]}...")


if __name__ == "__main__":
    main()
