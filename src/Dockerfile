FROM python:3

ENV PYTHONUNBUFFERED 1
ENV MOZ_HEADLESS=1

WORKDIR /app

COPY requirements.txt pyproject.toml /app/

RUN apt-get update \
    && apt-get install -y firefox-esr
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE "sunbottle.settings"
ENV DJANGO_SECRET_KEY "this is a secret key for building purposes"

RUN mkdir -p /opt/sunbottle/data
RUN mkdir -p /opt/sunbottle/.wdm
RUN chown -R www-data:www-data /opt/sunbottle

RUN python3 manage.py collectstatic --noinput

CMD uwsgi --ini sunbottle/interfaces/public/uwsgi.ini