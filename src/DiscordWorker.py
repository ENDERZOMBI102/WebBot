import asyncio
from asyncio import AbstractEventLoop, Future, Task
from os import getenv
from queue import Queue
from threading import Thread
from typing import Any, Coroutine

import discord

from cutypes import MayError
from logger import get_logger
import DataClasses


inboundMessageQueue: Queue[ DataClasses.Message ] = Queue()
outboundMessageQueue: Queue[ dict[ str, Any ] ] = Queue()
logger = get_logger( 'DiscordWorker' )


class DiscordWorker( discord.Client ):
	thread: Thread = None
	_instance: 'DiscordWorker'
	_checkerTask: Task

	def __init__( self ):
		loop = asyncio.new_event_loop()
		loop.set_debug( True )
		asyncio.set_event_loop( loop )
		super( DiscordWorker, self ).__init__(
			loop=loop
		)
		DiscordWorker._instance = self

	async def on_ready( self ) -> None:
		self._checkerTask = asyncio.create_task( self._checkQueue() )
		logger.info( f'Logged on as {self.user}!' )

	async def on_message( self, msg: discord.Message ) -> None:
		if msg.author.bot or msg.guild is None:
			return
		logger.info( f'Message from {msg.author}: "{msg.content}"' )
		inboundMessageQueue.put(
			DataClasses.Message(
				identifier=msg.id,
				content=msg.content,
				author=msg.author.id,
				channel=msg.channel.id,
				guild=msg.guild.id
			)
		)

	async def _checkQueue( self ) -> None:
		while True:
			await asyncio.sleep(2)
			for i in range( outboundMessageQueue.qsize() ):
				msg = outboundMessageQueue.get()
				await self.get_channel( msg[ 'channel' ] ).send( msg[ 'content' ] )
				outboundMessageQueue.task_done()

	async def _stop( self ):
		self._checkerTask.cancel()
		await self.close()
		self.loop.stop()

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
		logger.info( 'DiscordWorker shutting down!' )
		# stop the event loop
		asyncio.run_coroutine_threadsafe( DiscordWorker._stop, DiscordWorker.getInstance().getEventLoop() )
		# join the thread
		DiscordWorker.thread.join()

	@staticmethod
	def getInstance() -> 'DiscordWorker':
		""" Returns the current worker instance """
		return DiscordWorker._instance

	@staticmethod
	def runCoroutine( coro: Coroutine ) -> Future:
		"""
		Runs a coroutine and returns a future representing it

		This function is Threadsafe
		\f
		:param coro: coroutine to execute
		:return: future of the coroutine
		"""
		return asyncio.wrap_future(
			asyncio.run_coroutine_threadsafe( coro, DiscordWorker.getInstance().getEventLoop() )
		)

	# public methods
	def getEventLoop( self ) -> AbstractEventLoop:
		""" Returns the running event loop """
		return self.loop

	async def getMessage( self, channel: int, message: int ) -> MayError[DataClasses.Message]:
		"""
		Utility method to get a message from the channel and its id
		\f
		:param channel: channel to search into
		:param message: id of the message to search
		:return: the message if found
		"""
		try:
			msg: discord.Message = await ( await self.fetch_channel( channel ) ).fetch_message( message )
		except ( discord.NotFound, discord.Forbidden, discord.HTTPException ) as e:
			# handle exceptions the same way, but log different messages
			if isinstance(e, discord.NotFound):
				logger.error( f'Message with id {message} not found in channel with id {channel}!', e )
			elif isinstance(e, discord.Forbidden):
				logger.error( f'Access to channel with id {channel} is forbidden!', e )
			else:
				logger.error( f'Failed to get message with id {message} in channel {channel}!', e )
			return DataClasses.Error( code=e.status, message=e.text )
		else:
			return DataClasses.Message(
				identifier=message,
				content=msg.content,
				author=msg.author.id,
				channel=msg.channel.id,
				guild=msg.guild.id
			)

	async def getUser( self, user: int ) -> MayError[DataClasses.User]:
		"""
		Utility method to get a user from its id
		\f
		:param user: identifier of the user
		:return: the user if found
		"""
		try:
			usr: discord.User = await self.fetch_user(user)
		except ( discord.NotFound, discord.HTTPException ) as e:
			logger.error(f'Failed to get user with id {user}!', e)
			return DataClasses.Error( code=e.status, message=e.text )
		else:
			return DataClasses.User(
				identifier=user,
				username=usr.name,
				discriminator=usr.discriminator,
				is_bot=usr.bot
			)
