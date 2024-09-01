ARG python_version='3.10'
FROM python:${python_version}-alpine3.20

WORKDIR /api

ENV PIPENV_VENV_IN_PROJECT=1

RUN pip install pipenv
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install --system

COPY . .

CMD ["pipenv", "run", "python", "app.py"]
