FROM python:3.10

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

COPY . /app/

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "a_config.wsgi:application"]
