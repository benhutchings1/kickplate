# Kickplate API
The Kickplate API is the control plane for managing EDAGs and EDAG runs. To view the planned API specification visit https://editor.swagger.io/ and copy the contents of `docs/apispec.yml`

## Requirements
- Python 3.10
- Pipenv
- A compliant kubernetes cluster

## Usage
```
# In api directory
pipenv install
pipenv run dev
```
Visit `http://localhost:8080/docs#/` to view API specification. For more information please visit [Swagger UI Documentation Tool](https://swagger.io/tools/swagger-ui/)

### Modifications
To adjust API to the environment visit `settings.py` and modify parameters as needed