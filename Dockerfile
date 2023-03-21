FROM python:3.11-alpine

# install pip dependencies
WORKDIR /tmp
COPY ./src/requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# schedule script in crontab
WORKDIR /etc/cron.d

COPY ./crontab ./
RUN crontab crontab

CMD ["crond", "-f"]
