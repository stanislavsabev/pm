from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class UserV1(BaseModel):
    schema_version: Literal[1] = 1
    name: str
    email: str

class UserV2(BaseModel):
    schema_version: Literal[2] = 2
    first_name: str  # split from name
    last_name: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

## Migration Script Structure
"""
migrations/
├── __init__.py
├── runner.py          # core engine
├── registry.py        # migration registry
├── history.py         # applied migration tracking
└── versions/
    ├── __init__.py
    ├── v001_initial_schema.py
    ├── v002_split_user_name.py
    └── v003_add_user_timestamps.py
"""

# app code
# config
class Settings(BaseModel):
    auto_migrate: bool = False  # True in dev, always False in prod
    app_version: str = "1.3.0"
    environment: Literal["dev", "uat", "prod"] = "dev"