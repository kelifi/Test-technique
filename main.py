import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import psycopg2
from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel

# Define the SMTP server settings
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'houssempoly7@gmail.com'
smtp_password = 'ankzrdqfuaqwwsoq'

DB_HOST = '172.22.0.2'
DB_NAME = 'example_db'
DB_USER = 'postgres'
DB_PASSWORD = 'example'
DB_PORT = '5432'

app = FastAPI()

temp_db = {}


class User(BaseModel):
    name: str
    email: str


def create_tables():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.on_event("startup")
async def startup_event():
    create_tables()


@app.put('/user')
def create_user(user: User):
    """
    Create a new user in the database and send a verification email to the user.

    :param user: User object containing the user's name and email.
    :return: Created User object.
    """
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )

        # Check if the user already exists in the database
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (user.email,))
        count = cur.fetchone()[0]
        if count > 0:
            raise HTTPException(status_code=400, detail="User already exists")

        # Insert the user into the database
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (user.name, user.email)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Generate a 4-digit code for the user
        code = random.randint(1000, 9999)

        # Define the email content
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = user.email
        msg['Subject'] = 'Your verification code'
        body = f'This is your verification code is: {code}. Please input this code within one minute to complete the authentication process.'
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, user.email, msg.as_string())

        # Save the code and timestamp in a temporary dictionary
        temp_db[user.email] = {'code': str(code), 'timestamp': time.time()}

        # Return the created user
        return user

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/verify')
async def verify(email: str = Form(...), code: str = Form(...)):
    """
    Verify a user's email address by checking if the provided code matches the one
    sent to their email. If the code is correct and hasn't expired, the user is authenticated
    and a success message is returned. If the email or code are invalid or have expired, an
    HTTPException is raised with the appropriate status code and error message.

    Args:
        email (str): The email address of the user to verify.
        code (str): The code sent to the user's email to verify their address.

    Raises:
        HTTPException: If the email or code are invalid or have expired.

    Returns:
        A dictionary with a single key-value pair representing the success message.
    """
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )

        # Get the user with the specified email from the database
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # Check if the user exists
        if user is None:
            raise HTTPException(status_code=400, detail=f'Email {email} not found or code has expired.')

        # Check if the code is correct and hasn't expired
        if code != temp_db[email]['code']:
            raise HTTPException(status_code=400, detail='Incorrect code.')
        if time.time() - temp_db[email]['timestamp'] > 60:
            raise HTTPException(status_code=400, detail=f'Code for email {email} has expired.')

        # Delete the code cache for the user
        del temp_db[email]

        # Return a success message
        return {'message': f'Email {email} authenticated successfully.'}

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
