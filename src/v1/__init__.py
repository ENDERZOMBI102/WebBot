from fastapi import APIRouter

from . import messages, members

router = APIRouter(
	prefix="/v1"
)

router.include_router( messages.router )
router.include_router( members.router )
