FROM python@sha256:05b159167a0951570a7431c72ecd616cd0c3111a50ebee3191c36bafc20d2f80

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir pipenv \
    && pipenv install --system

CMD [ "python", "./main.py" ]
