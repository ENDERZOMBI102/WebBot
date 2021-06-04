from fastapi import APIRouter

from DataClasses import User

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
