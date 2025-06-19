from azure.servicebus import ServiceBusClient
from azure.identity import DefaultAzureCredential
import message_processor

SB_NAMESPACE = "yt-servicebus-ns.servicebus.windows.net"

def main():
    credential = DefaultAzureCredential()
    service_bus_client = ServiceBusClient(fully_qualified_namespace=SB_NAMESPACE ,credential=credential)
    with service_bus_client:
        receiver = service_bus_client.get_queue_receiver(queue_name="video-upload-completions")
        with receiver:
            for message in receiver.receive_messages(max_message_count=1, max_wait_time=300):
                print("Received message: {}".format(message))
                # acknowledge first, so that it is not processed again
                receiver.complete_message(message)
                # now process it
                message_processor.process_message(message)

main()