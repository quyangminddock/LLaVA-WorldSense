#!/usr/bin/env python3
"""Download LLaVA model weights from HuggingFace"""

from huggingface_hub import hf_hub_download
import os

print("Downloading LLaVA v1.5-7b model weights...")
print("This may take a while (model is ~13GB total)")

repo_id = "liuhaotian/llava-v1.5-7b"
files_to_download = [
    "pytorch_model-00001-of-00002.bin",
    "pytorch_model-00002-of-00002.bin",
    "pytorch_model.bin.index.json",
    "config.json",
    "generation_config.json",
    "tokenizer_config.json",
    "tokenizer.model",
    "special_tokens_map.json",
]

for filename in files_to_download:
    print(f"\n📥 Downloading {filename}...")
    try:
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir_use_symlinks=True
        )
        print(f"✅ Downloaded: {file_path}")
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")

print("\n" + "="*60)
print("✅ Download complete!")
print("="*60)
