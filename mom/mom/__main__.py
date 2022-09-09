import asyncio
import argparse

from . import  core

parser = argparse.ArgumentParser(description='Mother of Mirrors - Controller Daemon')
parser.add_argument('broker', type=str, help='address of MQTT broker')

args = parser.parse_args()

asyncio.run(core.run(args.broker))