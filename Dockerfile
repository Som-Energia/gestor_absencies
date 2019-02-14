FROM python:3
ENV PYTHONUNBUFFERED 1
WORKDIR /opt
COPY requirements.txt /opt/
RUN pip install -r requirements.txt
COPY config /opt/config
COPY gestor_absencies /opt/gestor_absencies
COPY manage.py /opt/

