FROM python:3.11

ENV POETRY_HOME=/opt/poetry
ENV POETRY_BIN=/opt/poetry/bin/poetry
ENV CRON_LOGS=/app/r6-calendar/logs/cron.log

COPY ./src ./app/r6-calendar
WORKDIR /app/r6-calendar

# install poetry
RUN wget -O /tmp/install-poetry.py https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/main/install-poetry.py && \
    python3 /tmp/install-poetry.py --version 1.6.1

# install dependencies
RUN ${POETRY_HOME}/bin/poetry install --only main

# schedule script in crontab
RUN apt update && apt install -y cron

# setup crontab
WORKDIR /etc/cron.d

COPY ./cron/r6_calendar_cron ./

RUN chmod 0644 r6_calendar_cron
RUN crontab r6_calendar_cron

CMD cron && ([ -f ${CRON_LOGS} ] || touch ${CRON_LOGS}; tail -f ${CRON_LOGS})
