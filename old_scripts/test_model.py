#!/usr/bin/env python3
"""
Script rapide pour tester un modèle fine-tuné avec LoRA
Usage: python test_model.py [chemin_vers_adaptateur] [prompt_optionnel]
"""

import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def test_model(adapter_path, prompt=None):
    """Teste un modèle fine-tuné avec LoRA"""
    
    print(f"🔄 Chargement du modèle de base...")
    base_model_name = "swiss-ai/Apertus-8B-Instruct-2509"
    
    # Charger le tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    
    # Charger le modèle de base
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        attn_implementation="flash_attention_2"
    )
    
    print(f"🔄 Chargement des adaptateurs LoRA depuis {adapter_path}...")
    # Charger les adaptateurs LoRA
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    
    # Prompt par défaut si non fourni
    if prompt is None:
        prompt = "Explique-moi ce qu'est le fine-tuning d'un modèle de langage en termes simples."
    
    print(f"\n💬 Prompt: {prompt}\n")
    print("=" * 80)
    
    # Préparer le message
    messages = [{"role": "user", "content": prompt}]
    
    # Appliquer le chat template
    input_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Tokenizer
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    
    # Générer
    print("🤖 Réponse du modèle:\n")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Décoder et afficher
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extraire seulement la réponse (après le prompt)
    if "<|im_start|>assistant" in response:
        response = response.split("<|im_start|>assistant")[-1].strip()
    
    print(response)
    print("\n" + "=" * 80)
    
    # Afficher les infos du modèle
    print(f"\n📊 Informations:")
    print(f"   - Modèle de base: {base_model_name}")
    print(f"   - Adaptateurs LoRA: {adapter_path}")
    print(f"   - Tokens générés: {outputs.shape[1] - inputs.input_ids.shape[1]}")
    print(f"   - Device: {model.device}")

if __name__ == "__main__":
    # Parser les arguments
    if len(sys.argv) < 2:
        print("❌ Usage: python test_model.py <chemin_adaptateur> [prompt]")
        print("\nExemple:")
        print("  python test_model.py Apertus-FT/output/apertus_lora_custom_001")
        print('  python test_model.py Apertus-FT/output/apertus_lora_custom_001 "Qu\'est-ce que l\'IA?"')
        sys.exit(1)
    
    adapter_path = sys.argv[1]
    prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    
    try:
        test_model(adapter_path, prompt)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
