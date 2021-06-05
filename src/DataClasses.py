from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


class Message( BaseModel ):
	identifier: int
	content: str
	author: int
	channel: int
	guild: int


class User( BaseModel ):
	identifier: int
	username: str
	discriminator: int
	is_bot: bool


class Member( BaseModel ):
	identifier: int
	nickname: Optional[ str ]
	roles: list[ int ]


class Role( BaseModel ):
	identifier: int
	name: str
	color: str


@dataclass
class Error:
	code: int
	message: str

	def __bool__( self ) -> bool:
		return False
