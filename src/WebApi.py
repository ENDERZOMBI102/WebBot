from fastapi import FastAPI

from logger import get_logger
import v1


logger = get_logger('WebAPI')
WebAPI = FastAPI(
	title='WebBot',
	version='1.0.0',
	docs_url='/',
	description='Request-based discord bot backend',
	on_startup=[ lambda: logger.info( 'Starting web API!' ) ],
	on_shutdown=[ lambda: logger.info( 'WebAPI shutting down!' ) ]
)

WebAPI.include_router( v1.router, prefix='/api' )
