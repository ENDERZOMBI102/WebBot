from fastapi import APIRouter, HTTPException

from DataClasses import Message
from DiscordWorker import inboundMessageQueue, outboundMessageQueue, DiscordWorker

router = APIRouter(
	tags=[ 'messages' ],
	responses={ 404: {'description': 'Not found'} },
)


@router.post( path='/messages' )
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


@router.get( path='/messages', response_model=list[Message] )
async def get_messages() -> list[ Message ]:
	""" Get all messages queued for processing. """
	msgs: list[Message] = []
	for i in range( inboundMessageQueue.qsize() ):
		msgs.append( inboundMessageQueue.get() )
		inboundMessageQueue.task_done()
	return msgs


@router.get( path='/messages/preview', response_model=list[Message] )
async def preview_messages() -> list[Message]:
	""" Get all messages queued for processing without removing them. """
	return [ *inboundMessageQueue.queue ]


@router.get( path='/messages/{identifier}', response_model=Message )
async def get_message( identifier: int, channel: int ) -> Message:
	"""
	Get a single message by its ID
	\f
	:param identifier:
	:param channel:
	:return:
	"""
	future = DiscordWorker.runCoroutine(
		DiscordWorker.getInstance().getMessage( channel, identifier )
	)
	await future

	if future.result():
		return future.result()
	raise HTTPException( future.result().code, future.result().message )
