FROM python:3.11

RUN mkdir /proctoring

WORKDIR /proctoring

COPY ../../ .

RUN pip install -r requirements/linux_reqs.txt

CMD fastapi dev src/main.py --port 9000 --host 0.0.0.0
