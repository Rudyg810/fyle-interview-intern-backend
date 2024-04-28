FROM python:3.8

ENV FLASK_APP="core/server.py"

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN flask db upgrade -d core/migrations/

EXPOSE 7755

CMD ["gunicorn", "-c", "gunicorn_config.py", "core.server:app"]
