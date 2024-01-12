FROM python:3.11

WORKDIR /usr/local/etc/lappy/

RUN apt-get update && apt-get install -y cron supervisor
COPY ./update_news /etc/cron.d/update_news
COPY ./cron.py .
RUN crontab /etc/cron.d/update_news

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./server ./server
COPY ./main.py .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT /usr/bin/supervisord
