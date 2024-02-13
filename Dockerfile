FROM python:3.11-slim

ENV TZ=Europe/Rome
ENV POETRY_HOME=/opt/poetry
ENV POETRY_BIN=/opt/poetry/bin/poetry
ENV CRON_LOGS=/app/r6-calendar/logs/cron.log

# install cron and tzdata, and setup timezone
RUN apt update && apt install -y cron wget tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./src/pyproject.toml ./src/poetry.lock /app/r6-calendar/
WORKDIR /app/r6-calendar

# install poetry
RUN wget -O /tmp/install-poetry.py https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/main/install-poetry.py && \
    python3 /tmp/install-poetry.py --version 1.7.1 && \
    ${POETRY_HOME}/bin/poetry install --only main

# setup crontab
WORKDIR /etc/cron.d
COPY ./cron/r6_calendar_cron ./
RUN chmod 0644 r6_calendar_cron && crontab r6_calendar_cron

CMD cron && ([ -f ${CRON_LOGS} ] || touch ${CRON_LOGS}; tail -f ${CRON_LOGS})
