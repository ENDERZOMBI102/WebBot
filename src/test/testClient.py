import time
from typing import Union

import requests


prefix = '!'
Message = dict[str, Union[str, int] ]


def getUrl(path) -> str:
	return f'http://localhost:5000/api/v1/{path}'


def sendMessage(message: str, channel: int) -> None:
	requests.post( getUrl(f'message?content={message}&channel={channel}') )


def handleMessage(content: str, identifier: int, author: int, channel: int, guild: int) -> None:
	if not content.startswith(prefix):
		return
	content = content.removeprefix(prefix)

	if content == 'helo':
		sendMessage( 'Hello there!', channel )
	else:
		sendMessage( 'Unknown command!', channel )


while True:
	time.sleep(2)
	obj: list[ Message ] = requests.get( getUrl('messages') ).json()
	for msg in obj:
		handleMessage(
			content=msg[ 'content' ],
			identifier=msg[ 'identifier' ],
			author=msg[ 'author' ],
			channel=msg[ 'channel' ],
			guild=msg[ 'guild' ]
		)
