from fastapi import FastAPI

from logger import get_logger
from v1 import v1APIRouter


logger = get_logger('WebAPI')
WebAPI = FastAPI(
	title='WebBot',
	version='1.0.0',
	description='Request-based discord bot backend',
	on_startup=[ lambda: logger.info( 'Starting web API!' ) ],
	on_shutdown=[ lambda: logger.info( 'WebAPI shutting down!' ) ]
)

WebAPI.include_router( v1APIRouter, prefix='/api/v1' )


@WebAPI.get( '/' )
async def root():
	return {
		'info': 'WebBot API',
		'message': 'Welcome to WebBot!',
		'docs-url': 'http://localhost:5000/docs'
	}
