import json
from pydantic import BaseModel

def schema_from_model(model: type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema(), indent=2)
