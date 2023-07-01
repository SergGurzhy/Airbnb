FROM python:3.11.4-alpine

COPY . /

RUN mkdir -p /source

RUN ["pip", "install", "-r", "requirements.txt"]

ENV SELENIUM_DRIVER_KIND="remote"
ENV REMOTE_DRIVER_HOST="localhost"
ENV SAVE_LOCAL="FALSE"
ENV BUCKET="bnbbucket-test"

ENV AWS_ACCESS_KEY_ID='AKIAQIBQSL2UWJ2NXXFA'
ENV AWS_SECRET_ACCESS_KEY='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'


CMD [ "python" ,"./main.py"]