from pydantic import BaseModel
from typing import Optional


class Post(BaseModel):
    title: str
    content: str
    user: str
    published: bool = True  # value by defect true
    rating: Optional[int] = None  # the attribute is optional allowing that user don't send this
    # if he doesn't want, and validates if the value is an integer

