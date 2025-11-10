from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema cho response sau khi login"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema cho data decode từ JWT token"""

    username: Optional[str] = None
