FROM python:3.11

WORKDIR /clickhouse

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

CMD ["python", "migrate.py"]