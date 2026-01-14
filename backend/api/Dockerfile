FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# COPY ../env ./env

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

