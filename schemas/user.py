from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class UserResponse(BaseModel):
    id: str
    username: str
    is_admin: bool
    must_change_password: bool

    model_config = ConfigDict(from_attributes=True)
