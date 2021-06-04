import uvicorn

from logger import init_logging, get_logger, logging
from DiscordWorker import DiscordWorker


init_logging(
	filename='./logs/latest.log'
)
logger = get_logger( 'WebBot' )
logging.getLogger('discord').setLevel(logging.INFO)


logger.info( 'Starting!' )
DiscordWorker.StartWorker()
uvicorn.run(
	app='WebApi:WebAPI',
	port=5000,
	host='127.0.0.1'
)

logger.info( 'Shutting down!' )
DiscordWorker.StopWorker()
logging.shutdown()
