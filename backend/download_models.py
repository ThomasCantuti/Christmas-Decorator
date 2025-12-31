import logging
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)


MODELS = {
    "vlm": {
        "repo_id": "unsloth/gemma-3-4b-it-GGUF",
        "filename": "gemma-3-4b-it-Q4_K_M.gguf",
        "mmproj_filename": "mmproj-F16.gguf",
        "description": "Gemma 3 4B for vision-language tasks",
    },
    # "diffusion": {
    #     "repo_id": "unsloth/Qwen-Image-Edit-2511-GGUF",
    #     "filename": "qwen-image-edit-2511-Q4_K_M.gguf",
    #     "description": "Qwen Image Edit for image editing tasks",
    # },
}


def get_available_files(repo_id: str) -> list[str]:
    """List available files in a Hugging Face repository."""
    try:
        files = list_repo_files(repo_id)
        return [f for f in files if f.endswith(".gguf")]
    except Exception as e:
        logger.warning(f"Could not list files: {e}")
        return []


def download_model(repo_id: str, filename: str, models_dir: Path) -> bool:
    """Download a model from Hugging Face."""
    try:
        target_path = models_dir / filename

        if target_path.exists():
            logger.info(f"{filename} already exists.")
            return True

        logger.info(f"Downloading {filename} from {repo_id}...")

        try:
            hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=models_dir,
            )
            logger.info(f"{filename} downloaded successfully.")
            return True
        except Exception:
            logger.warning(f"{filename} not found, searching for alternatives...")
            available_files = get_available_files(repo_id)

            if available_files:
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

                logger.info(f"Using alternative: {selected_file}")
                hf_hub_download(
                    repo_id=repo_id, filename=selected_file, local_dir=models_dir
                )
                logger.info(f"{selected_file} downloaded successfully.")
                return True
            else:
                logger.error(f"No GGUF files found in {repo_id}")
                return False

    except Exception as e:
        logger.error(f"Error downloading: {e}")
        return False


def download_models():
    """Download all required models for the Christmas Decorator application."""
    logger.info("🎄 Christmas Decorator - Model Download Script")
    logger.info("=" * 50)

    base_dir = Path(__file__).parent
    models_dir = base_dir / "models"
    models_dir.mkdir(exist_ok=True)

    logger.info(f"📂 Models directory: {models_dir}")
    logger.info("⬇️  Downloading models from Hugging Face (this may take a while)...")

    success_count = 0
    total_files = 0

    for key, config in MODELS.items():
        logger.info(f"📦 {key.upper()}: {config['description']}")
        total_files += 1
        if download_model(config["repo_id"], config["filename"], models_dir):
            success_count += 1

        if "mmproj_filename" in config:
            logger.info(f"Downloading mmproj for {key}...")
            total_files += 1
            if download_model(config["repo_id"], config["mmproj_filename"], models_dir):
                success_count += 1

    logger.info("=" * 50)
    if success_count == total_files:
        logger.info("🎉 All models downloaded successfully!")
        logger.info("You can now run the backend with: uvicorn main:app --reload")
    else:
        logger.warning(f"⚠️  {success_count}/{total_files} files downloaded.")
        logger.warning("Some models failed to download. Check the errors above.")


if __name__ == "__main__":
    download_models()
