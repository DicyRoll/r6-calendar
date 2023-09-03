FROM python:3.11

COPY ./src ./app/r6-calendar
WORKDIR /app/r6-calendar

# install poetry
ENV POETRY_HOME=/opt/poetry
RUN wget -O /tmp/install-poetry.py https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/main/install-poetry.py && \
    python3 /tmp/install-poetry.py --version 1.6.1

# install dependencies
RUN ${POETRY_HOME}/bin/poetry install --only main

# schedule script in crontab
RUN apt update && apt install -y cron

# setup crontab
RUN touch /app/r6-calendar/logs/cron.log

WORKDIR /etc/cron.d

COPY ./cron/r6_calendar_cron ./

RUN chmod 0644 r6_calendar_cron
RUN crontab r6_calendar_cron

CMD cron && tail -f /app/r6-calendar/logs/cron.log
