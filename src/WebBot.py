from logger import init_logging, get_logger, logging

import uvicorn

from WebApi import WebAPI
from DiscordWorker import DiscordWorker


init_logging(
	filename='/logs/latest.log'
)
logger = get_logger( 'WebBot' )


logger.info( 'Starting!' )
DiscordWorker.StartWorker()
uvicorn.run(
	app=WebAPI,
	port=5000
)

logger.info( 'Shutting down!' )
DiscordWorker.StopWorker()
logging.shutdown()
