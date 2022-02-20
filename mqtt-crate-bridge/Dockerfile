FROM python@sha256:e4e54a385b186ebc7e5f49b072185be8179ddbf7c05ea7c50009818b864e522a

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir pipenv \
  && pipenv install --system

CMD [ "python", "./main.py" ]
