FROM python:3.12.3-slim

WORKDIR /app
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./ ./

ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD python server.py
