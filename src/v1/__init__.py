from fastapi import APIRouter


v1APIRouter = APIRouter()


@v1APIRouter.get('')
async def getMessages():
	pass

