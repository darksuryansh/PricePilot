import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from transformers.cache_utils import DynamicCache

# Comprehensive monkey patch to fix DynamicCache compatibility issues with Phi-3
# The Phi-3 model expects older cache API methods that are missing in newer transformers versions

if not hasattr(DynamicCache, 'seen_tokens'):
    def get_seen_tokens(self):
        """Returns the number of tokens seen (processed) so far"""
        return self.get_seq_length()
    DynamicCache.seen_tokens = property(get_seen_tokens)

if not hasattr(DynamicCache, 'get_max_length'):
    def get_max_length(self):
        """Returns the maximum cache length. None means unlimited."""
        # Check if max_cache_len is set, otherwise return None (unlimited)
        if hasattr(self, 'max_cache_len') and self.max_cache_len is not None:
            return self.max_cache_len
        return None
    DynamicCache.get_max_length = get_max_length

if not hasattr(DynamicCache, 'get_usable_length'):
    def get_usable_length(self, seq_length, layer_idx=None):
        """Returns the usable length of the cache for a given sequence length"""
        # For initial generation, cache is empty, so return 0
        # For subsequent tokens, return the actual cache length
        cache_length = self.get_seq_length(layer_idx) if layer_idx is not None else self.get_seq_length()
        # Return the cache length directly, not the minimum
        return cache_length
    DynamicCache.get_usable_length = get_usable_length

# The official model identifier from Hugging Face
model_id = "microsoft/Phi-3-mini-4k-instruct"

# Modern Quantization Configuration
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True
)

# Updated Model Loading with multiple compatibility fixes
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cuda",
    quantization_config=bnb_config,
    trust_remote_code=True,
    attn_implementation="eager",  # Fix for the AttributeError
    dtype=torch.float16,         # Use dtype instead of torch_dtype
)



tokenizer = AutoTokenizer.from_pretrained(model_id)
print("Model loaded successfully!")

# Define the task for the model
review_text = (
    "The new laptop is fantastic. The screen is vibrant and the keyboard feels great to type on. "
    "I was able to get through a full workday on a single charge. However, the webcam quality is "
    "a bit disappointing for video calls, and it came with a lot of pre-installed bloatware I had to remove."
)

messages = [
    {"role": "system", "content": "You are an expert product review analyst. Your job is to extract the pros and cons from a review and list them clearly."},
    {"role": "user", "content": f"Please analyze the following review and give me the pros and cons:\n\n{review_text}"},
]

# Create a text-generation pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
)

# Set arguments for the generation process
generation_args = {
    "max_new_tokens": 500,
    "return_full_text": False,
    "temperature": 0.3,
    "do_sample": True,
    "pad_token_id": tokenizer.eos_token_id,  # Explicit pad token
    "past_key_values": None,  # Force clean cache initialization
}

print("\n--- Generating Response ---")
output = pipe(messages, **generation_args)
print(output[0]['generated_text'])
print("--- End of Response ---")