from core.event import ChannelEvent

channel = ChannelEvent()


async def outbound_webhook(data):
    print(f"\n[WEBHOOK OUT] Received event 'test_webhook' with data: {data}\n")
    # In a real scenario, this could send data to another external API


channel.subscribe_to("test_webhook", "after", outbound_webhook)