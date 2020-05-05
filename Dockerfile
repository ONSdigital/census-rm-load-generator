FROM python:3.7-slim

RUN pip install pipenv

RUN groupadd --gid 1000 loadgenerator && useradd --create-home --system --uid 1000 --gid loadgenerator loadgenerator
WORKDIR /home/loadgenerator

COPY Pipfile* /home/loadgenerator/
RUN pipenv install --system --deploy
USER loadgenerator

RUN mkdir /home/loadgenerator/.postgresql

COPY --chown=loadgenerator . /home/loadgenerator