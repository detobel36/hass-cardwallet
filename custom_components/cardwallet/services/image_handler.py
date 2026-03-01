import os
import uuid
import base64
from homeassistant.core import HomeAssistant

def _save_image_sync(storage_dir, content, file_ext):
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    filename = f"{uuid.uuid4()}{file_ext}"
    filepath = os.path.join(storage_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    return filename

async def save_image(hass: HomeAssistant, image_data) -> str:
    """Save image and return its URL."""
    storage_dir = hass.config.path("cardwallet_images")

    file_ext = ".png"
    content = None

    if isinstance(image_data, str):
        if image_data.startswith("http") or image_data.startswith("/api/cardwallet/images/"):
            return image_data
        if image_data.startswith("data:image/"):
            try:
                header, encoded = image_data.split(",", 1)
                file_ext = "." + header.split(";")[0].split("/")[1]
                content = base64.b64decode(encoded)
            except Exception:
                return None
    else:
        # aiohttp.web_request.FileField
        try:
            filename = image_data.filename
            file_ext = os.path.splitext(filename)[1]
            content = await hass.async_add_executor_job(image_data.file.read)
        except Exception:
            return None

    if content:
        filename = await hass.async_add_executor_job(_save_image_sync, storage_dir, content, file_ext)
        return f"/api/cardwallet/images/{filename}"

    return None

def _delete_image_sync(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)

async def delete_image(hass: HomeAssistant, image_url: str):
    """Delete local image file from URL."""
    if image_url and image_url.startswith("/api/cardwallet/images/"):
        image_name = image_url.split("/")[-1]
        image_path = hass.config.path("cardwallet_images", image_name)
        await hass.async_add_executor_job(_delete_image_sync, image_path)
