from python:3.10.14-alpine3.20
WORKDIR /api

run pip install pipenv
env PIPENV_VENV_IN_PROJECT=1
copy ./Pipfile .
copy ./Pipfile.lock .
run pipenv install

copy . .

CMD ["pipenv", "run", "python", "app.py"]
