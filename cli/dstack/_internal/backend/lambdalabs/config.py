from typing import Dict, List, Optional

from pydantic import BaseModel, ValidationError
from typing_extensions import Literal

from dstack._internal.backend.base.config import BackendConfig


class LambdaConfig(BackendConfig, BaseModel):
    backend: Literal["lambda"] = "lambda"
    regions: List[str]
    api_key: str

    def serialize(self) -> Dict:
        return self.dict()

    @classmethod
    def deserialize(cls, config_data: Dict) -> Optional["LambdaConfig"]:
        if config_data.get("backend") != "lambda":
            return None
        try:
            return cls.parse_obj(config_data)
        except ValidationError:
            return None
