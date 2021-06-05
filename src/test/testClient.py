import time

from requests import post, get


prefix = '!'


def getUrl(path) -> str:
	return f'http://localhost:5000/api/v1/{path}'


def sendMessage(message: str, channel: int) -> None:
	print(f'"{message}" -> {channel}')
	post( getUrl(f'messages?content={message}&channel={channel}') )


def handleMessage(content: str, identifier: int, author: int, channel: int, guild: int) -> None:
	if not content.startswith(prefix):
		return
	content = content.removeprefix(prefix)
	print(f'{guild}:{channel} -> "{content}"')

	if content == 'helo':
		sendMessage( 'Hello there!', channel )
	elif content.startswith('getmsg'):
		sendMessage(
			get(
				getUrl(f'messages/{content.removeprefix("getmsg ")}?channel={channel}')
			).json()['content'],
			channel
		)
	elif content.startswith('getusr'):
		sendMessage(
			get(
				getUrl(f'users/{content.removeprefix("getusr ")}')
			).text,
			channel
		)
	else:
		sendMessage( 'Unknown command!', channel )


while True:
	time.sleep(1)
	try:
		for msg in get( getUrl('messages') ).json():
			handleMessage(**msg)
	except ConnectionError:
		pass
