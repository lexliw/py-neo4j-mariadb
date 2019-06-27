FROM python:alpine3.9
COPY . /app
WORKDIR /app
RUN apk add gcc g++ make libffi-dev openssl-dev
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD python3 ./server.py
