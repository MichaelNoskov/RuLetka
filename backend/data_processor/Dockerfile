FROM python:3.11

WORKDIR /data_processor

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

CMD ["python", "main.py"]


# FROM python:3.12.3

# WORKDIR /data_processor

# COPY . .

# # Set up the virtual environment
# ENV PATH="/data_processor/venv/bin:$PATH"
# ENV VIRTUAL_ENV="/data_processor/venv"
# ENV PYTHONPATH="/data_processor/venv/lib/python3.13/site-packages"

# # Запускать приложение через python из venv
# # CMD ["python", "main.py"]
