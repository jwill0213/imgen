FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY requirements.txt /app/requirements.txt

RUN echo "wsgi-disable-file-wrapper = true" >> /etc/uwsgi/uwsgi.ini

RUN python3 -m pip install -r /app/requirements.txt

COPY ./ /app
