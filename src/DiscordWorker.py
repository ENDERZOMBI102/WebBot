import asyncio
from asyncio import AbstractEventLoop
from os import getenv
from queue import Queue
from threading import Thread

from discord import Client, Message

from logger import get_logger

messageQueue: Queue = Queue()
logger = get_logger('DiscordWorker')


class DiscordWorker(Client):

	thread: Thread = None
	_loop: AbstractEventLoop = None

	def __init__(self):
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		super(DiscordWorker, self).__init__(
			loop=loop
		)
		DiscordWorker._loop = loop

	async def on_ready(self):
		logger.info( f'Logged on as {self.user}!' )

	async def on_message(self, msg: Message):
		print( f'Message from {msg.author}: {msg.content}' )
		messageQueue.put(
			{
				'message': msg.content,
				'author': msg.author.id
			}
		)

	@staticmethod
	def StartWorker():
		logger.info( 'Starting DiscordWorker' )
		DiscordWorker.thread = Thread(
			target=lambda:
				DiscordWorker().run( getenv( 'TOKEN' ) )
		)
		DiscordWorker.thread.start()

	@staticmethod
	def StopWorker():
		logger.info('DiscordWorker shutting down!')
		# stop the event loop
		DiscordWorker._loop.call_soon_threadsafe( DiscordWorker._loop.stop )
		# join the thread
		DiscordWorker.thread.join()
