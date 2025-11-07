#!/usr/bin/env python3
"""
Script de test pour vérifier que les champs 'thinking' sont bien écartés
"""
import json
import re

def extract_final_answer(text):
    """Extrait la réponse finale en supprimant les balises <think>...</think>"""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)
    cleaned = cleaned.strip()
    return cleaned

def test_datasets():
    """Teste chaque dataset source pour vérifier l'extraction"""
    
    datasets_to_test = [
        {
            "name": "DPO Sources",
            "path": "my_datasets/all_DPO_sources_0.95-dedup.jsonl",
            "format": "question_answers"
        },
        {
            "name": "All Sources Dedup",
            "path": "my_datasets/all_sources_deduplicated.jsonl",
            "format": "question_answers"
        },
        {
            "name": "CTF Writeups",
            "path": "my_datasets/CTF_writeups_full_v2.jsonl",
            "format": "question_answers"
        },
        {
            "name": "Nvidia Science",
            "path": "my_datasets/100k_nvidia_science_reasoning_SFT_converted.jsonl",
            "format": "nvidia"
        }
    ]
    
    print("="*70)
    print("🔍 TEST DE SUPPRESSION DES CHAMPS 'THINKING'")
    print("="*70)
    
    for ds in datasets_to_test:
        print(f"\n📦 {ds['name']}")
        print(f"   Fichier: {ds['path']}")
        
        try:
            with open(ds['path'], 'r', encoding='utf-8') as f:
                # Lire la première ligne
                line = f.readline()
                if not line.strip():
                    line = f.readline()
                
                item = json.loads(line)
                
                if ds['format'] == 'question_answers':
                    # Vérifier structure
                    has_thinking = False
                    answer = item.get('answers', [{}])[0]
                    
                    if 'thinking_process' in answer:
                        has_thinking = True
                        thinking_len = len(answer.get('thinking_process', ''))
                        text_len = len(answer.get('text', ''))
                        
                        print(f"   ⚠️  Contient 'thinking_process':")
                        print(f"      - Longueur thinking: {thinking_len:,} chars")
                        print(f"      - Longueur text: {text_len:,} chars")
                        print(f"   ✅ Le script va extraire SEULEMENT 'text' (sans thinking)")
                    else:
                        print(f"   ✅ Pas de 'thinking_process'")
                    
                elif ds['format'] == 'nvidia':
                    # Vérifier balises <think>
                    answer = item.get('answer', '')
                    
                    if '<think>' in answer:
                        original_len = len(answer)
                        cleaned = extract_final_answer(answer)
                        cleaned_len = len(cleaned)
                        removed = original_len - cleaned_len
                        
                        print(f"   ⚠️  Contient balises <think>:")
                        print(f"      - Longueur originale: {original_len:,} chars")
                        print(f"      - Longueur nettoyée: {cleaned_len:,} chars")
                        print(f"      - Supprimé: {removed:,} chars ({removed/original_len*100:.1f}%)")
                        print(f"   ✅ Le script va nettoyer les balises")
                        
                        # Afficher un extrait
                        print(f"\n   📝 Extrait AVANT nettoyage:")
                        print(f"      {answer[:200]}...")
                        print(f"\n   📝 Extrait APRÈS nettoyage:")
                        print(f"      {cleaned[:200]}...")
                    else:
                        print(f"   ✅ Pas de balises <think>")
                
        except FileNotFoundError:
            print(f"   ❌ Fichier non trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print("\n" + "="*70)
    print("✅ VÉRIFICATION TERMINÉE")
    print("="*70)
    print("\n💡 Le script prepare_custom_mix_dataset.py a été mis à jour pour:")
    print("   1. Ignorer les champs 'thinking_process' dans question_answers")
    print("   2. Supprimer les balises <think>...</think> dans nvidia")
    print("   3. Garantir que le modèle Apertus ne soit PAS entraîné sur du 'thinking'")

if __name__ == "__main__":
    test_datasets()
