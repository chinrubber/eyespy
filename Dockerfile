FROM python:2

ENV FLASK_APP=wsgi.pi

WORKDIR /usr/src/app/eyespy

COPY eyespy/ /usr/src/app/eyespy/eyespy
COPY migrations/ /usr/src/app/eyespy/migrations
COPY manage.py /usr/src/app/eyespy/manage.py
COPY wsgi.py /usr/src/app/eyespy/wsgi.py
COPY requirements.txt /usr/src/app/eyespy/requirements.txt

RUN pip install -r requirements.txt

RUN rm /usr/src/app/eyespy/eyespy/data/eyespy.db

RUN python manage.py db upgrade

ENTRYPOINT [ "python", "manage.py", "runserver", "-p", "8000", "-h", "0.0.0.0", "-d" ]

EXPOSE 8000