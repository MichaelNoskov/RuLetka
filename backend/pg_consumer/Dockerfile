FROM python:3.11

WORKDIR /consumer

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# COPY ../env ./env

CMD ["uvicorn", "main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8090", "--workers=1"]