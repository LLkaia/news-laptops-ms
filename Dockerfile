FROM python:3.11

WORKDIR /usr/local/etc/lappy/
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./server ./server
COPY ./main.py .

CMD python3 main.py
