import asyncio
from asyncio import AbstractEventLoop, Future
from os import getenv
from queue import Queue
from threading import Thread
from typing import Any, Coroutine

from discord import Client, Message

from logger import get_logger
import DataClasses

inboundMessageQueue: Queue[Message] = Queue()
outboundMessageQueue: Queue[ dict[ str, Any ] ] = Queue()
logger = get_logger('DiscordWorker')


class DiscordWorker(Client):

	thread: Thread = None
	_instance: 'DiscordWorker'
	_loop: AbstractEventLoop = None

	def __init__(self):
		loop = asyncio.new_event_loop()
		loop.set_debug(True)
		asyncio.set_event_loop(loop)
		super(DiscordWorker, self).__init__(
			loop=loop
		)
		DiscordWorker._loop = loop
		DiscordWorker.INSTANCE = self
		loop.create_task( self.CheckOutboundQueue(), name='MessageSender' )

	async def on_ready(self) -> None:
		logger.info( f'Logged on as {self.user}!' )

	async def on_message(self, msg: Message) -> None:
		if msg.author.bot or msg.guild is None:
			return
		logger.info( f'Message from {msg.author}: {msg.content}' )
		inboundMessageQueue.put(
			DataClasses.Message(
				identifier=msg.id,
				content=msg.content,
				author=msg.author.id,
				channel=msg.channel.id,
				guild=msg.guild.id
			)
		)

	async def CheckOutboundQueue( self ) -> None:
		while True:
			await asyncio.sleep( 1 )
			for i in range( outboundMessageQueue.qsize() ):
				msg = outboundMessageQueue.get()
				await self.get_channel( msg['channel'] ).send( msg['content'] )
				outboundMessageQueue.task_done()

	@staticmethod
	def StartWorker() -> None:
		"""
		Start the worker in another thread

		The used token comes from the environment variable "TOKEN"
		"""
		logger.info( 'Starting DiscordWorker' )
		DiscordWorker.thread = Thread(
			target=lambda:
				DiscordWorker().run( getenv( 'TOKEN' ) )
		)
		DiscordWorker.thread.start()

	@staticmethod
	def StopWorker() -> None:
		""" Threadsafe static method to stop the worker """
		logger.info('DiscordWorker shutting down!')
		# stop the event loop
		DiscordWorker._loop.call_soon_threadsafe( DiscordWorker._loop.stop )
		# join the thread
		DiscordWorker.thread.join()

	@staticmethod
	def getEventLoop() -> AbstractEventLoop:
		""" Returns the running event loop """
		return DiscordWorker._loop

	@staticmethod
	def getInstance() -> 'DiscordWorker':
		return DiscordWorker._instance

	@staticmethod
	def runCoroutine( coro: Coroutine ) -> Future:
		"""
		Runs a coroutine and returns a future representing it

		This function is Threadsafe
		:param coro: coroutine to execute
		:return: future of the coroutine
		"""
		return asyncio.run_coroutine_threadsafe( coro, DiscordWorker.getEventLoop() )


