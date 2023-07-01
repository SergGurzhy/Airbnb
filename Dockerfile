FROM python:3.11.4-alpine

COPY . /

RUN mkdir -p /source

RUN ["pip", "install", "-r", "requirements.txt"]

ENV SELENIUM_DRIVER_KIND="remote"
ENV REMOTE_DRIVER_HOST="localhost"
ENV SAVE_LOCAL="FALSE"
ENV BUCKET="bnbbucket-test"

CMD [ "python" ,"./main.py"]