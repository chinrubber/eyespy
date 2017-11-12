FROM python:3

ENV FLASK_APP=wsgi.pi
ENV FLASK_DEBUG=0

WORKDIR /usr/src/app/eyespy

COPY eyespy/ /usr/src/app/eyespy/eyespy
COPY migrations/ /usr/src/app/eyespy/migrations
COPY manage.py /usr/src/app/eyespy/manage.py
COPY wsgi.py /usr/src/app/eyespy/wsgi.py
COPY requirements.txt /usr/src/app/eyespy/requirements.txt

RUN pip install -r requirements.txt

RUN rm -f /usr/src/app/eyespy/eyespy/data/eyespy.db

RUN mkdir /usr/src/app/eyespy/eyespy/data/db
RUN mkdir /usr/src/app/eyespy/eyespy/data/logs

RUN python3 manage.py db upgrade

ENTRYPOINT [ "python3", "manage.py", "runserver", "-p", "8000", "-h", "0.0.0.0" ]

EXPOSE 8000
