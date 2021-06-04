import asyncio

import discord
from fastapi import APIRouter

from DataClasses import Message
from DiscordWorker import inboundMessageQueue, outboundMessageQueue, DiscordWorker

router = APIRouter(
	prefix='/messages',
	tags=[ 'messages' ],
	responses={ 404: {'description': 'Not found'} },
)


@router.get( path='/', response_model=list[Message] )
async def get_messages() -> list[ Message ]:
	""" Get all messages queued for processing. """
	msgs: list[Message] = []
	for i in range( inboundMessageQueue.qsize() ):
		msgs.append( inboundMessageQueue.get() )
		inboundMessageQueue.task_done()
	return msgs


@router.get( path='/preview', response_model=list[Message] )
async def preview_messages() -> list[Message]:
	""" Get all messages queued for processing without removing them. """
	return [ *inboundMessageQueue.queue ]


@router.get( path='/{identifier}', response_model=Message )
async def get_message( identifier: int, channel: int ) -> Message:
	"""
	Get a single message by its ID
	\f
	:param identifier:
	:param channel:
	:return:
	"""
	async def getMessage() -> Message:
		msg: discord.Message = await ( await DiscordWorker.getInstance().fetch_channel(channel) ).fetch_message( identifier )
		return Message(
			identifier=msg.id,
			content=msg.content,
			author=msg.author.id,
			channel=msg.channel.id,
			guild=msg.guild.id
		)

	return await DiscordWorker.runCoroutine( getMessage() ).result()


@router.post( path='/' )
async def post_message( content: str, channel: int ) -> int:
	"""
	Sends a message to a specified channel.
	Returns the approximate position in the message queue
	- **content**: content of the message
	- **channel**: channel to send the message in
	\f
	:param content: content of the message
	:param channel: channel to send the message in
	:return: approximate position in the queue
	"""
	outboundMessageQueue.put(
		{
			'content': content,
			'channel': channel
		}
	)
	return outboundMessageQueue.qsize()
