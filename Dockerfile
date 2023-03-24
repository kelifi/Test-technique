FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=mysecretpassword \
    POSTGRES_HOST=db \
    POSTGRES_PORT=5432 \
    POSTGRES_DB=mydatabase

RUN pip install psycopg2-binary

EXPOSE 5000

CMD ["python", "main.py"]
