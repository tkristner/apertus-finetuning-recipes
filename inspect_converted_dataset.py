"""Inspect the converted dataset format."""
from datasets import load_from_disk
import json

# Load converted dataset
print("Loading converted dataset...")
ds = load_from_disk("./data/converted_dataset")

print(f"\nTrain size: {len(ds['train'])}")
print(f"Test size: {len(ds['test'])}")
print(f"Column names: {ds['train'].column_names}")

print(f"\nFirst training example:")
print(json.dumps(ds['train'][0], indent=2, ensure_ascii=False))

# Check structure
if 'messages' in ds['train'][0]:
    print("\n✅ Has 'messages' field")
    print(f"Number of messages: {len(ds['train'][0]['messages'])}")
    for i, msg in enumerate(ds['train'][0]['messages']):
        print(f"\nMessage {i}:")
        print(f"  Role: {msg.get('role', 'N/A')}")
        print(f"  Content length: {len(msg.get('content', ''))}")
elif 'text' in ds['train'][0]:
    print("\n✅ Has 'text' field")
else:
    print("\n⚠️ Has neither 'messages' nor 'text'!")
    print(f"Fields: {list(ds['train'][0].keys())}")
