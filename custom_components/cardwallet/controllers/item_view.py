from homeassistant.components.http import HomeAssistantView
from custom_components.cardwallet.services.storage import CardStorage
from custom_components.cardwallet.services.image_handler import save_image, delete_image

class CardWalletItemAPI(HomeAssistantView):
    url = "/api/cardwallet/{card_id}"
    name = "api:cardwallet:item"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass
        self.storage = CardStorage(hass)

    async def delete(self, request, card_id):
        data = await request.json()
        user_id = data.get("user_id")

        if not user_id or not card_id:
            return self.json({"error": "missing user_id or card_id"}, status_code=400)
        
        card = await self.storage.get_card_by_id(card_id)
        if not card:
            return self.json({"error": "card not found"}, status_code=404)
        
        if card.user_id != user_id:
            return self.json({"error": "not allowed to delete this card"}, status_code=403)

        deleted = await self.storage.delete_card(user_id, card_id)
        return self.json({"status": "deleted" if deleted else "not found"})


    async def put(self, request, card_id):
        if request.content_type == "application/json":
            data = await request.json()
        elif request.content_type == "multipart/form-data":
            data = await request.post()
            data = dict(data)
        else:
            return self.json({"error": "unsupported content type"}, status_code=400)

        user_id = data.get("user_id")

        if not user_id or not card_id:
            return self.json({"error": "missing user_id or card_id"}, status_code=400)

        card = await self.storage.get_card_by_id(card_id)
        if not card:
            return self.json({"error": "card not found"}, status_code=404)

        if card.user_id != user_id:
            return self.json({"error": "not allowed to update this card"}, status_code=403)

        image_data = data.get("image")
        if image_data:
            new_image = await save_image(self.hass, image_data)
            if new_image != card.image:
                # Delete old image if it was a local file and we have a new one
                if card.image:
                    await delete_image(self.hass, card.image)
                data["image"] = new_image
            else:
                # If same image, just use it (or it's already in card.image)
                data["image"] = card.image

        updated = await self.storage.update_card(user_id, card_id, data)
        if updated:
            return self.json(updated.__dict__)
        return self.json({"error": "card not found"}, status_code=404)