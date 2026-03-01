import os
import homeassistant.helpers.config_validation as cv
from .api import CardWalletListAPI, CardWalletItemAPI
from .services.storage import CardStorage

DOMAIN = "cardwallet"
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

async def async_setup(hass, config):
    storage = CardStorage(hass)
    await storage.load()

    hass.http.register_view(CardWalletListAPI(hass))
    hass.http.register_view(CardWalletItemAPI(hass))

    image_path = hass.config.path("cardwallet_images")
    if not os.path.exists(image_path):
        await hass.async_add_executor_job(os.makedirs, image_path)

    hass.http.register_static_path("/api/cardwallet/images", image_path, auth_required=True)

    return True