import asyncio
import signal

import gmqtt


async def run(broker_host: str):
    will_message = gmqtt.Message('pick_n_plaser/stop', True)
    client = gmqtt.Client("mom", will_message=will_message)
    
    await client.connect(broker_host)
    
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def stop(*args):
        stop_event.set()
        
    loop.add_signal_handler(signal.SIGINT, stop)
    loop.add_signal_handler(signal.SIGTERM, stop)

    client.publish('pick_n_plaser/stop', False)
    client.publish('pick_n_plaser/coordinates', (0, 0, 0, 0))

    await stop_event.wait()

    await client.disconnect(reason_code=4, reason_string="MoM was forced to quit")

