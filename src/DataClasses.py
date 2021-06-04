from pydantic import BaseModel


class Message(BaseModel):
	identifier: int
	content: str
	author: int
	channel: int
	guild: int


class User(BaseModel):
	identifier: int
	nickname: str
	discriminator: int

