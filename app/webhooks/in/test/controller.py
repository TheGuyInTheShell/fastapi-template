from fastapi import APIRouter
from core.event import ChannelEvent

router = APIRouter()
channel = ChannelEvent()

@router.post("/")
async def inbound_webhook(data: dict):
    try:
        # Emit event to the channel
        channel.emit_to("test_webhook").run(data)
        return {"status": "event_emitted", "data": data}
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
