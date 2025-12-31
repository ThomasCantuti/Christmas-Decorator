import torch
from diffusers import QwenImageEditPlusPipeline
from app.services.images import ImageService
from pathlib import Path

image_service = ImageService()


class LLMService:
    def __init__(self):
        pass

    def load_model(self) -> QwenImageEditPlusPipeline:
        pipeline = QwenImageEditPlusPipeline.from_pretrained(
            pretrained_model_name_or_path="Qwen/Qwen-Image-Edit-2511",
            torch_dtype=torch.bfloat16,
        )
        if pipeline is None:
            raise RuntimeError("Failed to load QwenImageEditPlusPipeline model")
        if torch.cuda.is_available():
            pipeline.to("cuda")
        elif torch.mps.is_available():
            pipeline.to("mps")
        else:
            pipeline.to("cpu")
        return pipeline

    def unload_model(self, pipeline: QwenImageEditPlusPipeline):
        pipeline.to("cpu")

    def edit_image(self, pipeline: QwenImageEditPlusPipeline, image: Path, prompt: str) -> Path:
        pil_image = image_service.get_pil_image(image)
        pipeline.set_progress_bar_config(disable=None)
        inputs = {
            "image": [pil_image],
            "prompt": prompt,
            "generator": torch.manual_seed(0),
            "true_cfg_scale": 4.0,
            "negative_prompt": " ",
            "num_inference_steps": 40,
            "guidance_scale": 1.0,
            "num_images_per_prompt": 1,
        }

        with torch.inference_mode():
            output = pipeline(**inputs)
            output_image = output.images[0]
            return image_service.save_pil_image(output_image, "output.jpg")
