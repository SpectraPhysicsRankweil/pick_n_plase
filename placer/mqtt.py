import asyncio
import signal
import atexit
import json

import gmqtt
from placer import Placer


async def run(broker_host: str, placer_callback):
    will_message = gmqtt.Message('pick_n_plaser/stop', True)
    # client = gmqtt.Client("mom", will_message=will_message)
    client = gmqtt.Client("placer")

    await client.connect(broker_host)

    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def stop(*args):
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, stop)
    loop.add_signal_handler(signal.SIGTERM, stop)

    client.subscribe('pick_n_plaser/coordinates')

    client.on_message = placer_callback

    await stop_event.wait()

    await client.disconnect(reason_code=4, reason_string="Placer was forced to quit")


def on_message(client, topic, payload, qos, properties):
    print('RECV MSG:', payload)


if __name__ == "__main__":
    placer = Placer()
    atexit.register(placer.exit_handler)

    def placer_callback(client, topic, payload, qos, properties):
        coordinates = json.loads(payload.decode())
        print('RECV:', coordinates)
        placer.position_and_rotate(*coordinates)

    asyncio.run(run('10.0.1.156', placer_callback))


