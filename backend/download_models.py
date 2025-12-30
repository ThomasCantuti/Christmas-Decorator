"""
Model Download Script

This script downloads and prepares all models required by the Christmas Decorator
application. Models are configured to match those used in agents.py:
- Text: unsloth/gemma-3-270m-it-GGUF
- VLM: unsloth/gemma-3-4b-it-GGUF
- Diffusion: unsloth/Qwen-Image-Edit-2511-GGUF

Models are downloaded from Hugging Face and stored locally.
"""

from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files


# Model configurations matching agents.py DEFAULT_CLIENTS
MODELS = {
    "text": {
        "repo_id": "unsloth/gemma-3-270m-it-GGUF",
        "filename": "gemma-3-270m-it-Q4_K_M.gguf",  # Q4_K_M quantization for good balance
        "description": "Gemma 3 270M for text processing",
    },
    "vlm": {
        "repo_id": "unsloth/gemma-3-4b-it-GGUF",
        "filename": "gemma-3-4b-it-Q4_K_M.gguf",  # Q4_K_M quantization
        "mmproj_filename": "mmproj-F16.gguf", # Required for vision capabilities
        "description": "Gemma 3 4B for vision-language tasks",
    },
    "diffusion": {
        "repo_id": "unsloth/Qwen-Image-Edit-2511-GGUF",
        "filename": "Qwen-Image-Edit-2511-Q4_K_M.gguf",  # Q4_K_M quantization
        "description": "Qwen Image Edit for image editing tasks",
    },
}


def get_available_files(repo_id: str) -> list[str]:
    """List available files in a Hugging Face repository."""
    try:
        files = list_repo_files(repo_id)
        return [f for f in files if f.endswith(".gguf")]
    except Exception as e:
        print(f"   ⚠️  Could not list files: {e}")
        return []


def download_model(repo_id: str, filename: str, models_dir: Path) -> bool:
    """Download a model from Hugging Face."""
    try:
        target_path = models_dir / filename
        
        if target_path.exists():
            print(f"   ✅ {filename} already exists.")
            return True
        
        print(f"   Downloading {filename} from {repo_id}...")
        
        # Try to download the specified file
        try:
            hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=models_dir,
            )
            print(f"   ✅ {filename} downloaded successfully.")
            return True
        except Exception as e:
            # If specific file not found, try to find an alternative
            print(f"   ⚠️  {filename} not found, searching for alternatives...")
            available_files = get_available_files(repo_id)
            
            if available_files:
                # Prefer Q4_K_M, then Q4_K, then any Q4, then first available
                preferred_order = ["Q4_K_M", "Q4_K", "Q4", "Q8", "Q5"]
                selected_file: str | None = None
                
                for pref in preferred_order:
                    for f in available_files:
                        if pref in f:
                            selected_file = f
                            break
                    if selected_file is not None:
                        break
                
                if selected_file is None:
                    selected_file = available_files[0]
                
                print(f"   Using alternative: {selected_file}")
                hf_hub_download(
                    repo_id=repo_id,
                    filename=selected_file,
                    local_dir=models_dir
                )
                print(f"   ✅ {selected_file} downloaded successfully.")
                return True
            else:
                print(f"   ❌ No GGUF files found in {repo_id}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error downloading: {e}")
        return False


def download_models():
    """Download all required models for the Christmas Decorator application."""
    print("🎄 Christmas Decorator - Model Download Script")
    print("=" * 50)
    
    # Define paths
    base_dir = Path(__file__).parent
    models_dir = base_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    print(f"\n📂 Models directory: {models_dir}")
    
    # Download each model
    print("\n⬇️  Downloading models from Hugging Face (this may take a while)...")
    
    success_count = 0
    total_files = 0
    
    for key, config in MODELS.items():
        print(f"\n📦 {key.upper()}: {config['description']}")
        total_files += 1
        if download_model(config["repo_id"], config["filename"], models_dir):
            success_count += 1
            
        # Check for mmproj (multimodal projector)
        if "mmproj_filename" in config:
            print(f"   ... downloading mmproj for {key} ...")
            total_files += 1
            if download_model(config["repo_id"], config["mmproj_filename"], models_dir):
                success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    if success_count == total_files:
        print("🎉 All models downloaded successfully!")
        print("   You can now run the backend with: uvicorn main:app --reload")
    else:
        print(f"⚠️  {success_count}/{total_files} files downloaded.")
        print("   Some models failed to download. Check the errors above.")


if __name__ == "__main__":
    download_models()
