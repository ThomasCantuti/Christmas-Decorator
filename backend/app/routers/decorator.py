from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.schemas import DecorateResponse
from app.services.agents import AgentService
from app.services.images import ImageService
import logging
import base64
from pathlib import Path
from typing import Optional
from datapizza.type.type import TextBlock, MediaBlock, Media

logger = logging.getLogger(__name__)
agent_service = AgentService()
image_service = ImageService()
router = APIRouter()


@router.post("/api/decorate", response_model=DecorateResponse)
async def decorate_image(
    image: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
):
    """
    Decorate an uploaded image with Christmas themes.

    This endpoint orchestrates a multi-agent pipeline:
    1. Image Validation
    2. Text Validation (optional)
    3. Decoration Planning and Image Generation
    """

    file_path: Optional[Path] = None

    try:
        image_service.check_image(image)
        file_path = await image_service.save_image(image)

        # ========== Image Validation ==========
        validation_prompt = (
            "Is this image showing an indoor environment like a room, office, "
            "or living space that could be decorated for Christmas? "
            "Answer with YES or NO and a brief reason."
        )

        image_validation_result = list(
            agent_service.get_validate_image_agent().stream_invoke(
                task_input=[
                    TextBlock(content=validation_prompt),
                    MediaBlock(
                        media=Media(
                            media_type="image",
                            source_type="path",
                            source=str(file_path),
                        )
                    ),
                ],
            )
        )[-1]

        logger.info(f"Image validation result: {image_validation_result.text}")

        validation_response = image_validation_result.text.strip().upper()
        if (
            validation_response.startswith("NO")
            or "NO," in validation_response[:10]
            or "NO." in validation_response[:10]
        ):
            error_reason = image_validation_result.text
            logger.warning(f"Image validation failed: {error_reason}")
            raise HTTPException(
                status_code=400,
                detail=f"Image validation failed: {error_reason}. Please upload a clear photo of an indoor room, office, or living space.",
            )

        # ========== Text Validation ==========
        if prompt:
            text_validation_prompt = (
                f"The user wants to: '{prompt}'. "
                "Is this request relevant and achievable for decorating this image? "
                "Answer with YES or NO and a brief reason."
            )

            text_validation_result = list(
                agent_service.get_validate_text_agent().stream_invoke(
                    task_input=[
                        TextBlock(content=text_validation_prompt),
                        MediaBlock(
                            media=Media(
                                media_type="image",
                                source_type="path",
                                source=str(file_path),
                            )
                        ),
                    ],
                )
            )[-1]

            logger.info(f"Text validation result: {text_validation_result.text}")

            text_validation_response = text_validation_result.text.strip().upper()
            if (
                text_validation_response.startswith("NO")
                or "NO," in text_validation_response[:10]
                or "NO." in text_validation_response[:10]
            ):
                error_reason = text_validation_result.text
                logger.warning(f"Text validation failed: {error_reason}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Prompt validation failed: {error_reason}. Please try a request specifically related to Christmas decorations.",
                )

        # ========== Decoration Planning and Image Generation ==========
        if prompt:
            planning_message = f"The user provided the following request: '{prompt}'."
        else:
            planning_message = "The user did not provide a request."

        # Use content_type from upload to determine extension/subtype for Google Agent
        # (This avoids "Unsupported MIME type: image/None" when file has no extension)
        mime_subtype = "jpeg"
        if image.content_type and "/" in image.content_type:
            mime_subtype = image.content_type.split("/")[-1].split(";")[0]

        decoration_result = list(
            agent_service.get_decorator_agent().stream_invoke(
                task_input=[
                    TextBlock(content=planning_message),
                    MediaBlock(
                        media=Media(
                            media_type="image",
                            source_type="path",
                            source=str(file_path),
                            extension=mime_subtype,
                        )
                    ),
                ],
            )
        )[-1]

        logger.info("Decoration result received.")

        image_data = None
        explanation_text = ""

        explanation_text = (
            decoration_result.text if hasattr(decoration_result, "text") else ""
        )

        for block in decoration_result.content:
            if isinstance(block, MediaBlock):
                media = block.media
                logger.info(f"Found MediaBlock with source_type: {media.source_type}")

                if media.source_type == "base64":
                    logger.info("Found base64 media block from agent.")
                    if isinstance(media.source, str):
                        image_data = media.source
                    else:
                        image_data = base64.b64encode(media.source).decode("utf-8")
                break

        if image_data is None:
            logger.warning(
                "No image found in decoration result, returning original image"
            )
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            explanation_text = explanation_text or "Unable to generate decorated image"

        return DecorateResponse(
            image_base64=image_data,
            explanation=explanation_text or "Image decorated successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        logger.error(f"Decoration failed: {error_str}", exc_info=True)

        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            raise HTTPException(
                status_code=429,
                detail="Google Gemini API quota exceeded. Please wait a minute before trying again.",
            )

        raise HTTPException(
            status_code=500, detail=f"Failed to decorate image: {error_str}"
        )

    finally:
        if file_path and file_path.exists():
            file_path.unlink()
