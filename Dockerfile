FROM python:3

WORKDIR /usr/src/app/eyespy

COPY ./ /usr/src/app/eyespy

RUN pip install --requirement requirements.txt; \
    mkdir /usr/src/app/eyespy/eyespy/data

ENTRYPOINT [ "gunicorn", "wsgi", "--bind=0.0.0.0:8080", "--access-logfile=-", "--config=" ]

EXPOSE 8080
