FROM alpine:latest

RUN apk add --no-cache python3

ADD src/ShellyForHassProxy.py /opt/proxy.py

ENV PYTHONUNBUFFERED=0
ENTRYPOINT ["python3", "-u", "/opt/proxy.py"]