"""Check if tokenizer has chat template configured."""
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("swiss-ai/Apertus-8B-Instruct-2509")

print(f"Tokenizer class: {tokenizer.__class__.__name__}")
print(f"Has chat_template: {hasattr(tokenizer, 'chat_template')}")
if hasattr(tokenizer, 'chat_template'):
    print(f"Chat template: {tokenizer.chat_template}")
else:
    print("⚠️  No chat template found!")

# Test with a sample message
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"}
]

try:
    formatted = tokenizer.apply_chat_template(messages, tokenize=False)
    print(f"\n✅ Chat template works!")
    print(f"Formatted output:\n{formatted}")
except Exception as e:
    print(f"\n❌ Error applying chat template: {e}")
