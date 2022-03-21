FROM python:3.8

WORKDIR /app
COPY requirements.txt /app
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt --no-cache-dir
COPY foodgram/ /app
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
