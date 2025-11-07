# Copyright 2020-2025 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
accelerate launch \
    --config_file configs/zero3.yaml \
    sft_train.py \
    --config configs/sft_lora.yaml \
    --model_name_or_path swiss-ai/Apertus-8B-Instruct-2509 \
"""

from datasets import load_dataset, load_from_disk
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from trl import (
    ModelConfig,
    ScriptArguments,
    SFTConfig,
    SFTTrainer,
    TrlParser,
    get_peft_config,
)
from training_logger import AutomatedTrainingLogger



def main(script_args, training_args, model_args, config_file_path=None):
    # ------------------------
    # Add timestamp to output directory
    # ------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_output_dir = training_args.output_dir
    training_args.output_dir = f"{original_output_dir}_{timestamp}"
    print(f"📁 Output directory: {training_args.output_dir}")

    # ------------------------
    # Save training configuration at startup
    # ------------------------
    os.makedirs(training_args.output_dir, exist_ok=True)

    # Sauvegarder la config YAML utilisée
    config_backup_dir = os.path.join(training_args.output_dir, 'config_backup')
    os.makedirs(config_backup_dir, exist_ok=True)

    # Copier la config YAML si elle existe
    if config_file_path and os.path.exists(config_file_path):
        shutil.copy(config_file_path, os.path.join(config_backup_dir, os.path.basename(config_file_path)))
        print(f"✅ Config YAML sauvegardée: {os.path.join(config_backup_dir, os.path.basename(config_file_path))}")
    else:
        print(f"⚠️  Aucune config YAML à sauvegarder (config_file_path={config_file_path})")

    # Sauvegarder les arguments de training en JSON
    training_params = {
        'timestamp': timestamp,
        'model': {
            'name_or_path': model_args.model_name_or_path,
            'dtype': str(model_args.dtype),
            'attn_implementation': model_args.attn_implementation,
        },
        'dataset': {
            'name': script_args.dataset_name,
            'train_split': script_args.dataset_train_split,
            'test_split': script_args.dataset_test_split,
        },
        'training': {
            'learning_rate': training_args.learning_rate,
            'num_train_epochs': training_args.num_train_epochs,
            'per_device_train_batch_size': training_args.per_device_train_batch_size,
            'gradient_accumulation_steps': training_args.gradient_accumulation_steps,
            'warmup_ratio': training_args.warmup_ratio,
            'lr_scheduler_type': training_args.lr_scheduler_type,
            'max_grad_norm': training_args.max_grad_norm,
            'logging_steps': training_args.logging_steps,
            'eval_strategy': training_args.eval_strategy,
            'save_strategy': training_args.save_strategy,
            'save_steps': training_args.save_steps,
            'seed': training_args.seed,
            'output_dir': training_args.output_dir,
        }
    }

    params_file = os.path.join(training_args.output_dir, 'training_parameters.json')
    with open(params_file, 'w', encoding='utf-8') as f:
        json.dump(training_params, f, indent=2, ensure_ascii=False)
    print(f"✅ Paramètres sauvegardés: {params_file}")
    
    # ------------------------
    # Load model & tokenizer
    # ------------------------
    #Set base directory to store model
    store_base_dir = "./" #os.getenv("STORE")


    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        dtype=model_args.dtype,
        use_cache=False if training_args.gradient_checkpointing else True,
        attn_implementation=model_args.attn_implementation,   # <-- ensure it’s used
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
    )
    tokenizer.pad_token = tokenizer.eos_token

    # --------------
    # Load dataset
    # --------------
    # Support both HuggingFace Hub datasets and local datasets
    if os.path.exists(script_args.dataset_name):
        # Load from local directory
        if script_args.dataset_name.endswith('.jsonl') or script_args.dataset_name.endswith('.json'):
            # Load from JSONL/JSON file
            dataset = load_dataset("json", data_files=script_args.dataset_name)
            print(f"✅ Loaded dataset from JSON file: {script_args.dataset_name}")
        elif os.path.isdir(script_args.dataset_name):
            # Load from disk (saved with save_to_disk)
            dataset = load_from_disk(script_args.dataset_name)
            print(f"✅ Loaded dataset from disk: {script_args.dataset_name}")
        else:
            raise ValueError(f"Unknown dataset format: {script_args.dataset_name}")
    else:
        # Load from HuggingFace Hub
        dataset = load_dataset(script_args.dataset_name, name=script_args.dataset_config)
        print(f"✅ Loaded dataset from HuggingFace Hub: {script_args.dataset_name}")

    # -------------
    # Train model
    # -------------
    # Créer le callback de logging automatique
    logging_callback = AutomatedTrainingLogger()

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset[script_args.dataset_train_split],
        eval_dataset=dataset[script_args.dataset_test_split]
        if training_args.eval_strategy != "no"
        else None,
        processing_class=tokenizer,
        peft_config=get_peft_config(model_args),
        callbacks=[logging_callback],  # Ajouter le callback
    )

    trainer.train()
    trainer.save_model(os.path.join(store_base_dir, training_args.output_dir))
    if training_args.push_to_hub:
        trainer.push_to_hub(dataset_name=script_args.dataset_name)


if __name__ == "__main__":
    import sys
    
    # Capturer le chemin du fichier de config depuis les arguments
    config_file_path = None
    for i, arg in enumerate(sys.argv):
        if arg == '--config' and i + 1 < len(sys.argv):
            config_file_path = sys.argv[i + 1]
            break
    
    parser = TrlParser((ScriptArguments, SFTConfig, ModelConfig))
    script_args, training_args, model_args, _ = parser.parse_args_and_config(
        return_remaining_strings=True
    )
    main(script_args, training_args, model_args, config_file_path)