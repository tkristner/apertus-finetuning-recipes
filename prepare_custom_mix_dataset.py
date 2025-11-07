#!/usr/bin/env python3
"""
Crée un dataset mixé selon l'Option C:
- 60% Cybersécurité:
    - 40% All Sources Deduplicated (mix optimal cyber)
    - 20% GDPR/Privacy (all_DPO_sources)
- 40% Diversification:
    - 25% Nvidia Science Reasoning
    - 10% Code (CodeAlpaca)
    - 5% Créatif/Chat (Dolly)

Le script valide que les sources ont assez d'exemples pour respecter les ratios.
"""

import json
import random
import sys
import re
from datasets import load_dataset, Dataset, DatasetDict
from pathlib import Path
from tqdm import tqdm


class DatasetSource:
    """Représente une source de données avec ses métadonnées"""

    def __init__(self, name, path, ratio, source_type, format_type):
        self.name = name
        self.path = path
        self.ratio = ratio
        self.source_type = source_type  # 'local' ou 'huggingface'
        self.format_type = format_type  # 'question_answers', 'messages', 'nvidia', 'dpo', etc.
        self.available_count = 0
        self.required_count = 0
        self.data = []


def count_jsonl_lines(filepath):
    """Compte le nombre de lignes dans un fichier JSONL"""
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def extract_final_answer(text):
    """
    Extrait la réponse finale en supprimant les balises <think>...</think>
    et tout le raisonnement intermédiaire.
    
    Args:
        text: Texte pouvant contenir des balises <think>
    
    Returns:
        Texte nettoyé sans les sections de thinking
    """
    # Supprimer toutes les balises <think>...</think> et leur contenu
    # Pattern: <think> ... </think> (non-greedy)
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Nettoyer les espaces multiples et les sauts de ligne excessifs
    cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned


def load_local_jsonl(source, max_samples=None):
    """
    Charge un fichier JSONL local et convertit au format messages

    Args:
        source: DatasetSource object
        max_samples: Nombre max d'exemples à charger (None = tous)

    Returns:
        Liste d'exemples au format messages
    """
    print(f"   📂 Chargement de {source.path}...")

    data = []
    with open(source.path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if max_samples and i >= max_samples:
                break

            if not line.strip():
                continue

            try:
                item = json.loads(line)

                # Convertir selon le format
                if source.format_type == 'question_answers':
                    # Format: {"question": "...", "answers": [...]}
                    question = item.get('question', '')

                    # Trouver la réponse choisie
                    chosen_answer = None
                    for answer in item.get('answers', []):
                        if answer.get('type') == 'chosen' or answer.get('score', 0) >= 1.0:
                            chosen_answer = answer
                            break

                    if not chosen_answer and item.get('answers'):
                        chosen_answer = item['answers'][0]

                    if not chosen_answer or not question:
                        continue
                    
                    # ⚠️ IMPORTANT: Extraire uniquement le champ 'text', PAS 'thinking_process'
                    # Le modèle Apertus n'est PAS un modèle de type "thinking"
                    answer_text = chosen_answer.get('text', '')
                    if not answer_text:
                        continue

                    # Déterminer le system prompt selon la source
                    if 'dpo' in source.name.lower() or 'gdpr' in source.name.lower():
                        system_prompt = "You are a helpful AI assistant specialized in data protection, privacy compliance, and GDPR regulations."
                    elif 'ctf' in source.name.lower():
                        system_prompt = "You are a skilled cybersecurity professional specialized in CTF challenges, penetration testing, and security assessments."
                    elif 'cyber' in source.name.lower() or 'redteam' in source.name.lower():
                        system_prompt = "You are an advanced cybersecurity expert specialized in offensive security, red teaming, and threat analysis."
                    else:
                        system_prompt = "You are a helpful AI assistant specialized in cybersecurity and information security."

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer_text}  # Seulement le texte, sans thinking_process
                    ]

                elif source.format_type == 'messages':
                    # Déjà au bon format
                    if 'messages' not in item:
                        continue
                    messages = item['messages']

                elif source.format_type == 'nvidia':
                    # Format Nvidia: {"question": "...", "answer": "...", "reasoning": "...", ...}
                    question = item.get('question', '')
                    answer = item.get('answer', '')

                    if not question or not answer:
                        continue

                    # Nettoyer les balises <think> du dataset Nvidia
                    clean_answer = extract_final_answer(answer)
                    
                    # Vérifier qu'il reste une réponse après nettoyage
                    if not clean_answer or len(clean_answer.strip()) < 10:
                        # Si la réponse est trop courte après nettoyage, garder l'originale
                        # (peut arriver si toute la réponse était dans <think>)
                        clean_answer = answer

                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful AI assistant specialized in scientific reasoning and problem-solving. Think step by step and provide detailed explanations."
                        },
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": clean_answer}
                    ]

                elif source.format_type == 'dpo':
                    # Format DPO: {"system": "...", "prompt": "...", "chosen": "...", "rejected": "..."}
                    system = item.get('system', 'You are a helpful AI assistant specialized in cybersecurity.')
                    prompt = item.get('prompt', '')
                    chosen = item.get('chosen', '')

                    if not prompt or not chosen:
                        continue

                    messages = [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": chosen}
                    ]

                else:
                    print(f"   ⚠️  Format inconnu: {source.format_type}")
                    continue

                data.append({
                    'messages': messages,
                    'source': source.name
                })

            except Exception as e:
                # Ignorer les lignes problématiques
                continue

    print(f"   ✅ {len(data)} exemples chargés")
    return data


def load_huggingface_dataset(source, max_samples):
    """Charge un dataset depuis HuggingFace"""
    print(f"   📥 Téléchargement depuis HuggingFace: {source.path}...")

    try:
        if source.name == 'code':
            dataset = load_dataset("sahil2801/CodeAlpaca-20k", split="train")

            # Limiter au max_samples
            if len(dataset) > max_samples:
                indices = random.sample(range(len(dataset)), max_samples)
                dataset = dataset.select(indices)

            data = []
            for example in tqdm(dataset, desc="   Conversion"):
                instruction = example.get("instruction", "")
                input_text = example.get("input", "")
                output = example.get("output", "")

                if not instruction or not output:
                    continue

                user_content = instruction
                if input_text:
                    user_content += f"\n\nInput:\n{input_text}"

                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant specialized in software development and coding. Provide clear, efficient, and well-documented code solutions."
                    },
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": output}
                ]

                data.append({
                    'messages': messages,
                    'source': source.name
                })

        elif source.name == 'general':
            dataset = load_dataset("databricks/databricks-dolly-15k", split="train")

            # Limiter au max_samples
            if len(dataset) > max_samples:
                indices = random.sample(range(len(dataset)), max_samples)
                dataset = dataset.select(indices)

            data = []
            for example in tqdm(dataset, desc="   Conversion"):
                instruction = example.get("instruction", "")
                context = example.get("context", "")
                response = example.get("response", "")

                if not instruction or not response:
                    continue

                user_content = instruction
                if context:
                    user_content += f"\n\nContext:\n{context}"

                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful, creative, and knowledgeable AI assistant. Provide informative and engaging responses."
                    },
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": response}
                ]

                data.append({
                    'messages': messages,
                    'source': source.name
                })

        print(f"   ✅ {len(data)} exemples convertis")
        return data

    except Exception as e:
        print(f"   ❌ Erreur lors du chargement: {e}")
        return []


def validate_sources(sources, target_total):
    """
    Valide que les sources ont assez d'exemples pour respecter les ratios

    Returns:
        (bool, str): (succès, message d'erreur éventuel)
    """
    print("\n" + "="*70)
    print("🔍 VALIDATION DES SOURCES")
    print("="*70)

    all_valid = True
    error_messages = []

    for source in sources:
        required = int(target_total * source.ratio)
        source.required_count = required

        # Compter les exemples disponibles
        if source.source_type == 'local':
            if not Path(source.path).exists():
                error_messages.append(f"❌ Fichier introuvable: {source.path}")
                all_valid = False
                continue

            source.available_count = count_jsonl_lines(source.path)
        else:
            # Pour HuggingFace, on estime (sera vérifié au chargement)
            if source.name == 'code':
                source.available_count = 20000
            elif source.name == 'general':
                source.available_count = 15000

        status = "✅" if source.available_count >= required else "❌"
        print(f"\n{status} {source.name}")
        print(f"   Ratio: {source.ratio*100:.1f}%")
        print(f"   Requis: {required:,} exemples")
        print(f"   Disponible: {source.available_count:,} exemples")

        if source.available_count < required:
            error_messages.append(
                f"❌ {source.name}: Insuffisant ({source.available_count:,} < {required:,})"
            )
            all_valid = False

    if not all_valid:
        print("\n" + "="*70)
        print("❌ VALIDATION ÉCHOUÉE")
        print("="*70)
        for msg in error_messages:
            print(msg)
        print("\n💡 Solutions:")
        print("   1. Réduire le nombre total d'exemples (--target-total)")
        print("   2. Ajuster les ratios")
        print("   3. Ajouter plus de données sources")
        return False, "\n".join(error_messages)

    print("\n" + "="*70)
    print("✅ VALIDATION RÉUSSIE - Toutes les sources sont suffisantes")
    print("="*70)
    return True, ""


def create_mixed_dataset(sources, target_total, output_dir, seed=42):
    """
    Crée le dataset mixé

    Args:
        sources: Liste de DatasetSource
        target_total: Nombre total d'exemples
        output_dir: Répertoire de sortie
        seed: Seed pour la reproductibilité
    """
    random.seed(seed)

    print("\n" + "="*70)
    print("🎯 CRÉATION DU DATASET MIXÉ")
    print("="*70)

    all_data = []

    # Charger chaque source
    for source in sources:
        print(f"\n📦 Traitement: {source.name}")

        if source.source_type == 'local':
            data = load_local_jsonl(source, max_samples=source.required_count * 2)
        else:
            data = load_huggingface_dataset(source, max_samples=source.required_count * 2)

        # Échantillonner au nombre requis
        if len(data) > source.required_count:
            data = random.sample(data, source.required_count)
            print(f"   🔀 Échantillonné à {source.required_count} exemples")
        elif len(data) < source.required_count:
            print(f"   ⚠️  Seulement {len(data)} exemples disponibles (requis: {source.required_count})")

        source.data = data
        all_data.extend(data)

    # Mélanger
    print(f"\n🔀 Mélange de {len(all_data)} exemples...")
    random.shuffle(all_data)

    # Statistiques
    source_counts = {}
    for item in all_data:
        src = item.get('source', 'unknown')
        source_counts[src] = source_counts.get(src, 0) + 1

    print(f"\n📊 STATISTIQUES FINALES:")
    print(f"   Total: {len(all_data):,} exemples")
    for src, count in sorted(source_counts.items()):
        ratio = count / len(all_data) * 100 if len(all_data) > 0 else 0
        print(f"   - {src:30} {count:6,} ({ratio:5.1f}%)")

    # Sauvegarder en JSONL
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / "train.jsonl"
    print(f"\n💾 Sauvegarde JSONL: {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"✅ Sauvegardé!")

    # Convertir au format HuggingFace
    print(f"\n🔄 Conversion au format HuggingFace...")

    dataset = Dataset.from_list(all_data)

    # Split train/test (90/10)
    split_dataset = dataset.train_test_split(
        test_size=0.1,
        seed=seed,
        shuffle=True
    )

    dataset_dict = DatasetDict({
        "train": split_dataset["train"],
        "test": split_dataset["test"]
    })

    # Sauvegarder
    hf_output_dir = output_path.parent / f"{output_path.name}_hf"
    hf_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"💾 Sauvegarde HuggingFace: {hf_output_dir}...")
    dataset_dict.save_to_disk(str(hf_output_dir))

    print(f"\n🎉 Dataset HuggingFace créé:")
    print(f"   - Train: {len(dataset_dict['train']):,} exemples")
    print(f"   - Test: {len(dataset_dict['test']):,} exemples")

    # Afficher des exemples
    print(f"\n📋 EXEMPLES PAR SOURCE:")
    for src_name in sorted(source_counts.keys()):
        examples = [item for item in all_data if item.get('source') == src_name]
        if examples:
            ex = examples[0]
            print(f"\n   [{src_name.upper()}]")
            print(f"   System: {ex['messages'][0]['content'][:70]}...")
            print(f"   User: {ex['messages'][1]['content'][:80]}...")
            print(f"   Assistant: {ex['messages'][2]['content'][:80]}...")

    print(f"\n{'='*70}")
    print(f"✅ DATASET PRÊT!")
    print(f"{'='*70}")
    print(f"\n📝 Pour l'utiliser dans le fine-tuning:")
    print(f"   1. Modifiez configs/sft_lora_combined.yaml:")
    print(f"      dataset_name: {hf_output_dir}")
    print(f"   2. Lancez: apertus sft configs/sft_lora_combined.yaml")
    print(f"\n💡 Fichiers créés:")
    print(f"   - JSONL: {output_file}")
    print(f"   - HuggingFace: {hf_output_dir}")

    return hf_output_dir


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Crée un dataset mixé selon l'Option C",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Option C - Répartition:
  60% Cybersécurité:
    - 40% All Sources Deduplicated (mix cyber optimal)
    - 20% GDPR/Privacy (all_DPO_sources)
  40% Diversification:
    - 25% Nvidia Science Reasoning
    - 10% Code (CodeAlpaca)
    - 5% Créatif/Chat (Dolly)

Exemple d'utilisation:
  python prepare_custom_mix_dataset.py --target-total 30000
  python prepare_custom_mix_dataset.py --target-total 10000 --output ./data/my_mix
        """
    )

    parser.add_argument(
        "--target-total",
        type=int,
        required=True,
        help="Nombre TOTAL d'exemples souhaités dans le dataset final"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="./data/custom_mix_dataset",
        help="Répertoire de sortie (défaut: ./data/custom_mix_dataset)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed pour la reproductibilité (défaut: 42)"
    )

    parser.add_argument(
        "--cyber-dedup",
        type=str,
        default="my_datasets/all_sources_deduplicated.jsonl",
        help="Chemin vers all_sources_deduplicated.jsonl"
    )

    parser.add_argument(
        "--dpo-sources",
        type=str,
        default="my_datasets/all_DPO_sources_0.95-dedup.jsonl",
        help="Chemin vers all_DPO_sources_0.95-dedup.jsonl"
    )

    parser.add_argument(
        "--nvidia-reasoning",
        type=str,
        default="my_datasets/100k_nvidia_science_reasoning_SFT_converted.jsonl",
        help="Chemin vers 100k_nvidia_science_reasoning_SFT_converted.jsonl"
    )

    args = parser.parse_args()

    # Définir les sources selon Option C
    sources = [
        DatasetSource(
            name="cyber_dedup",
            path=args.cyber_dedup,
            ratio=0.40,  # 40% du total
            source_type='local',
            format_type='question_answers'
        ),
        DatasetSource(
            name="dpo_privacy",
            path=args.dpo_sources,
            ratio=0.20,  # 20% du total
            source_type='local',
            format_type='question_answers'
        ),
        DatasetSource(
            name="nvidia_science",
            path=args.nvidia_reasoning,
            ratio=0.25,  # 25% du total
            source_type='local',
            format_type='nvidia'
        ),
        DatasetSource(
            name="code",
            path="sahil2801/CodeAlpaca-20k",
            ratio=0.10,  # 10% du total
            source_type='huggingface',
            format_type='hf_code'
        ),
        DatasetSource(
            name="general",
            path="databricks/databricks-dolly-15k",
            ratio=0.05,  # 5% du total
            source_type='huggingface',
            format_type='hf_general'
        ),
    ]

    # Vérifier que les ratios somment à 1.0
    total_ratio = sum(s.ratio for s in sources)
    if abs(total_ratio - 1.0) > 0.01:
        print(f"❌ Erreur: La somme des ratios ({total_ratio:.2f}) != 1.0")
        sys.exit(1)

    print("="*70)
    print("🎯 PRÉPARATION DU DATASET MIXÉ - OPTION C")
    print("="*70)
    print(f"\nCible: {args.target_total:,} exemples")
    print(f"\nRépartition:")
    print(f"  60% Cybersécurité:")
    print(f"    - 40% All Sources Deduplicated")
    print(f"    - 20% GDPR/Privacy")
    print(f"  40% Diversification:")
    print(f"    - 25% Nvidia Science Reasoning")
    print(f"    - 10% Code (CodeAlpaca)")
    print(f"    - 5% Général (Dolly)")

    # Valider les sources
    valid, error_msg = validate_sources(sources, args.target_total)

    if not valid:
        print(f"\n❌ Impossible de créer le dataset avec {args.target_total:,} exemples")
        sys.exit(1)

    # Créer le dataset
    output_dir = create_mixed_dataset(
        sources=sources,
        target_total=args.target_total,
        output_dir=args.output,
        seed=args.seed
    )


if __name__ == "__main__":
    main()
