"""Inspect the original Multilingual-Thinking dataset format."""
from datasets import load_dataset
import json

# Load original dataset
print("Loading HuggingFaceH4/Multilingual-Thinking...")
ds = load_dataset("HuggingFaceH4/Multilingual-Thinking", split="train")

print(f"\nDataset size: {len(ds)}")
print(f"Column names: {ds.column_names}")
print(f"\nFirst example:")
print(json.dumps(ds[0], indent=2, ensure_ascii=False))

# Check if it has 'messages' or 'text' field
if 'messages' in ds[0]:
    print("\n✅ Dataset has 'messages' field")
    print(f"Messages structure:")
    for msg in ds[0]['messages']:
        print(f"  - Role: {msg.get('role', 'N/A')}")
        if 'content' in msg:
            print(f"    Content: {msg['content'][:100]}...")
        if 'thinking' in msg:
            print(f"    Thinking: {msg['thinking'][:100]}...")
elif 'text' in ds[0]:
    print("\n✅ Dataset has 'text' field")
    print(f"Text preview: {ds[0]['text'][:200]}...")
else:
    print("\n⚠️ Dataset has neither 'messages' nor 'text' field!")
    print(f"Available fields: {list(ds[0].keys())}")
