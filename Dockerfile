FROM python:3

WORKDIR /usr/src/app

COPY ./ /usr/src/app

RUN pip install --requirement requirements.txt

ENTRYPOINT [ "gunicorn", "wsgi", "--bind=0.0.0.0:8080", "--access-logfile=-", "--config=" ]

EXPOSE 8080
