"""
Convert custom JSONL dataset to HuggingFace format for SFT training.
"""
import json
from datasets import Dataset, DatasetDict
from pathlib import Path


def convert_to_chat_format(example):
    """
    Convert your JSONL format to chat messages format.
    
    Your format has:
    - question: str
    - answers: list with chosen/rejected answers
    
    We'll convert to OpenAI chat format with system/user/assistant messages.
    """
    question = example["question"]
    
    # Get the chosen answer (score = 1.0)
    chosen_answer = None
    for answer in example["answers"]:
        if answer.get("type") == "chosen" or answer.get("score", 0) >= 1.0:
            chosen_answer = answer
            break
    
    if not chosen_answer:
        # Fallback to first answer if no chosen found
        chosen_answer = example["answers"][0]
    
    # Create chat messages in the format expected by the model
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant specialized in data protection and privacy compliance."
        },
        {
            "role": "user",
            "content": question
        },
        {
            "role": "assistant",
            "content": chosen_answer["text"]
        }
    ]
    
    return {"messages": messages}


def load_and_convert_dataset(jsonl_path, train_split=0.9):
    """
    Load JSONL file and convert to HuggingFace dataset format.
    
    Args:
        jsonl_path: Path to your JSONL file
        train_split: Proportion of data to use for training (rest for validation)
    
    Returns:
        DatasetDict with train and test splits
    """
    # Load JSONL
    data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    print(f"Loaded {len(data)} examples from {jsonl_path}")
    
    # Convert to chat format
    converted_data = [convert_to_chat_format(example) for example in data]
    
    # Create dataset
    dataset = Dataset.from_list(converted_data)
    
    # Split into train/test
    split_dataset = dataset.train_test_split(
        test_size=1 - train_split,
        seed=42
    )
    
    return DatasetDict({
        "train": split_dataset["train"],
        "test": split_dataset["test"]
    })


def main():
    # Example usage
    jsonl_path = "my_datasets/all_DPO_sources_0.95-dedup.jsonl"  # UPDATE THIS PATH
    
    # Convert and save
    dataset = load_and_convert_dataset(jsonl_path)
    
    # Save to disk in HuggingFace format
    output_dir = "./data/converted_dataset"
    dataset.save_to_disk(output_dir)
    
    print(f"\nDataset saved to {output_dir}")
    print(f"Train examples: {len(dataset['train'])}")
    print(f"Test examples: {len(dataset['test'])}")
    print("\nExample message format:")
    print(dataset['train'][0])


if __name__ == "__main__":
    main()
