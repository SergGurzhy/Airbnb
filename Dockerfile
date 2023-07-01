FROM python:3.11.4-alpine

COPY . /

RUN mkdir -p /source

RUN ["pip", "install", "-r", "requirements.txt"]

ARG PARAM_1
ARG PARAM_2
ARG PARAM_3

ENV SELENIUM_DRIVER_KIND="remote"
ENV REMOTE_DRIVER_HOST="localhost"
ENV SAVE_LOCAL="FALSE"
ENV BUCKET=$PARAM_1
ENV AWS_ACCESS_KEY_ID=$PARAM_2
ENV AWS_SECRET_ACCESS_KEY=$PARAM_3

CMD [ "python" ,"./main.py"]