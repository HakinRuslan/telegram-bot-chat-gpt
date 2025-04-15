FROM python:3.12
EXPOSE 8000
ENV HOME=/opt/app
WORKDIR /opt/app

COPY req.txt /tmp/requirements.txt
COPY botapp .

RUN pip install virtualenv  &&\
    python -m virtualenv /opt/venv &&\
    chown 1001:1001 /opt/ -R

USER 1001

RUN . /opt/venv/bin/activate &&\
    pip install pip --upgrade &&\
    pip install -r  /tmp/requirements.txt &&\
    cd /opt/app/ && ls -li


CMD . /opt/venv/bin/activate && cd /opt/app/ &&python bot_run.py
#&& uvicorn main:app --host 0.0.0.0