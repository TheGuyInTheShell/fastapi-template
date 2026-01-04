from core.event import ChannelEvent, event_result
channel = ChannelEvent()


async def outbound_webhook(data, result=channel.DependsEvent(event_result)):
    print(f"\n[WEBHOOK OUT] Received event 'test_webhook'")
    print(f"Data: {data}")
    print(f"Result from controller: {result}\n")
    # In a real scenario, this could send data to another external API


channel.subscribe_to("test_webhook", "after", outbound_webhook)