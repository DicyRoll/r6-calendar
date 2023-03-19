FROM python:3.11

WORKDIR /tmp

COPY ./src/requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
