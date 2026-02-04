"""
CLI module generator for creating FastAPI webhook structures.
"""
import os
from pathlib import Path


def create_in_controller_template(name: str) -> str:
    """Generate controller.py template for inbound webhooks"""
    return f'''from fastapi import APIRouter
from core.event import ChannelEvent

router = APIRouter()
channel = ChannelEvent()

@router.post("/")
async def inbound_{name}_webhook(data: dict):
    """
    Handle inbound webhook for {name}.
    Emits a channel event that can be subscribed to by other parts of the system.
    """
    try:
        # Emit event to the channel
        channel.emit_to("{name}_webhook").run(data)
        return {{"status": "event_emitted", "data": data}}
    except Exception as e:
        import traceback
        return {{"status": "error", "error": str(e), "traceback": traceback.format_exc()}}
'''


def create_out_subscriber_template(name: str) -> str:
    """Generate subscriber.py template for outbound webhooks"""
    return f'''from core.event import ChannelEvent, event_result
channel = ChannelEvent()


async def outbound_{name}_webhook(data, result=channel.DependsEvent(event_result)):
    """
    Handle outbound webhook for {name}.
    This is triggered after a "{name}_webhook" event is emitted.
    """
    print(f"\\n[WEBHOOK OUT] Received event '{name}_webhook'")
    print(f"Data: {{data}}")
    print(f"Result from emitter: {{result}}\\n")
    
    # Logic to send data to an external service would go here
    # Example:
    # import httpx
    # async with httpx.AsyncClient() as client:
    #     await client.post("https://external-service.com/webhook", json=data)


# Subscribe to the event
channel.subscribe_to("{name}_webhook", "after", outbound_{name}_webhook)
'''


def generate_webhook(name: str, direction: str = 'both'):
    """
    Generate webhook structures.
    direction: 'in', 'out', or 'both'
    """
    # Get the project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    
    if direction in ['in', 'both']:
        in_path = project_root / "app" / "webhooks" / "in" / name
        in_path.mkdir(parents=True, exist_ok=True)
        print(f"[+] Created directory: {in_path}")
        
        init_file = in_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            
        controller_file = in_path / "controller.py"
        if not controller_file.exists():
            with open(controller_file, 'w', encoding='utf-8') as f:
                f.write(create_in_controller_template(name))
            print(f"[OK] Created: {controller_file.relative_to(project_root)}")

    if direction in ['out', 'both']:
        out_path = project_root / "app" / "webhooks" / "out" / name
        out_path.mkdir(parents=True, exist_ok=True)
        print(f"[+] Created directory: {out_path}")
        
        init_file = out_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            
        subscriber_file = out_path / "subscriber.py"
        if not subscriber_file.exists():
            with open(subscriber_file, 'w', encoding='utf-8') as f:
                f.write(create_out_subscriber_template(name))
            print(f"[OK] Created: {subscriber_file.relative_to(project_root)}")

    print(f"\n[SUCCESS] Webhook '{name}' ({direction}) generated successfully!")
