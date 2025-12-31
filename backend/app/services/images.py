from fastapi import UploadFile
from logging import Logger
from pathlib import Path
from PIL.Image import Image

logger = Logger(__name__)


class ImageService:
    def __init__(self):
        self.input_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir = Path(__file__).resolve().parent.parent.parent / "processed"
        self.output_dir.mkdir(exist_ok=True)
        self.file_extension = None

    def check_image(self, image: UploadFile) -> None:
        if not image.filename:
            image.filename = "image.jpg"
        if Path(image.filename).suffix not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
        }:
            self.file_extension = ".jpg"
        else:
            self.file_extension = Path(image.filename).suffix

    async def save_image(self, image: UploadFile) -> Path:
        filename = image.filename or "image.jpg"
        with open(self.input_dir / Path(filename).name, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        logger.info(f"Saved uploaded image to {self.input_dir / Path(filename).name}")
        return self.input_dir / Path(filename).name

    def get_pil_image(self, image_path: Path):
        from PIL import Image

        return Image.open(image_path)

    def save_pil_image(self, image: Image, filename: str) -> Path:
        self.output_dir.mkdir(exist_ok=True)
        with open(self.output_dir / filename, "wb") as buffer:
            image.save(buffer, "JPEG")
        logger.info(f"Saved processed image to {self.output_dir / filename}")
        return self.output_dir / filename
