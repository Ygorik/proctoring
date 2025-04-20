FROM python:3.11

# Установка CMake и build-essential
RUN apt-get update && \
    apt-get install -y cmake build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /proctoring

WORKDIR /proctoring

COPY ../../ .

RUN pip install -r requirements/linux_reqs.txt

CMD fastapi dev src/main.py --port 9000 --host 0.0.0.0
