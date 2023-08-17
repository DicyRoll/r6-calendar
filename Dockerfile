FROM python:3.11-alpine

COPY ./src ./app/r6-calendar
WORKDIR /app/r6-calendar

RUN apk update
RUN apk add curl

# install poetry
RUN export POETRY_HOME=/ && curl -sSL https://install.python-poetry.org | python3 -

# install dependencies
RUN poetry install --only main

# schedule script in crontab
WORKDIR /etc/cron.d

COPY ./cron/r6_calendar_cron ./
RUN crontab r6_calendar_cron

CMD ["crond", "-f"]
