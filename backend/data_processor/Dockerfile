FROM python:3.11

WORKDIR /data_processor

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

CMD ["python", "main.py"]