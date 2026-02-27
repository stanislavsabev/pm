from pydantic import BaseModel, Field
from typing import ClassVar


class VersionedDocument(BaseModel):
    schema_version: int = Field(exclude=True)

    model_config = ConfigDict(
        populate_by_name=True,  # useful when loading from Mongo dicts
    )

    def to_mongo(self) -> dict:
        doc = self.model_dump()
        doc["schema_version"] = self.schema_version
        return doc

    @classmethod
    def from_mongo(cls, data: dict) -> "VersionedDocument":
        return cls.model_validate(data)

class UserV2(VersionedDocument):
    schema_version: int = Field(default=2, exclude=True)
    _expected_version: ClassVar[int] = 2

    first_name: str
    last_name: str
    email: str