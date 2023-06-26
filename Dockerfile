FROM python:3.9

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./main.py .
COPY ./templates ./templates

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
