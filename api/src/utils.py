from kubernetes import client, config
from kubernetes.dynamic import DynamicClient
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def validate_against_schema(json_schema:dict, json_def:str) -> tuple[bool, str]:
    try:
        validate(instance=json_def, schema=json_schema)
        return (True, True) # Double up to preserve tuple consistency
    except ValidationError as e:
        return (False, e)
    except e:
        return (False, "Schema validation error")


def read_schema(path:str) -> dict:
    with open(path, "r") as fs:
        return json.loads(fs.read())


def connect_to_kubenetes() -> DynamicClient:
    config.load_kube_config()
    return DynamicClient(client.ApiClient())