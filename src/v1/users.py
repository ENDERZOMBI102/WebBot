from fastapi import APIRouter, HTTPException

from DataClasses import User
from DiscordWorker import DiscordWorker

router = APIRouter(
	prefix='/users',
	tags=[ 'users' ],
	responses={ 404: {'description': 'Not found'} },
)


@router.get( path='/{identifier}', response_model=User )
async def get_user(identifier: int) -> User:
	"""
	Get an user from its ID
	\f
	:param identifier:
	:return:
	"""
	future = DiscordWorker.runCoroutine(
		DiscordWorker.getInstance().getUser( identifier )
	)
	await future

	if future.result():
		return future.result()
	raise HTTPException( future.result().code, future.result().message )

