from fastapi import APIRouter

from . import messages, users

router = APIRouter(
	prefix="/v1"
)

router.include_router( messages.router )
router.include_router( users.router )
