# Email Verification API

This is a simple FastAPI-based API that allows users to 
create accounts and verify their email addresses by sending 
a 4-digit code to their email and prompting them to enter 
the code within one minute. The API uses PostgreSQL as the database to store user information.
user has only one minute to use this code. After that, an error should be raised.

## Installation
1. Clone the repository: git clone ``` https://github.com/your-username/email-verification-api.git ```

2. Install the required packages: ``` pip install -r requirements.txt``` 
3. Set the required environment variables:

    * DB_HOST: the host of the PostgreSQL database
    * DB_NAME: the name of the PostgreSQL database
    * DB_USER: the username to connect to the PostgreSQL database
    * DB_PASSWORD: the password to connect to the PostgreSQL database
    * DB_PORT: the port to use to connect to the PostgreSQL database
    * SMTP_USERNAME: the username to connect to the SMTP server
    * SMTP_PASSWORD: the password to connect to the SMTP server

4. Start the API: uvicorn main:app --reload

## Usage

### Create a new user

To create a new user, send a PUT request to /user with a JSON payload containing the user's name and email:

```python
PUT /user HTTP/1.1
Content-Type: application/json

{
  "name": "John Doe",
  "email": "johndoe@example.com"
}

```

If the email is not already in use, the API will create a new user in the database and send a verification code to the specified email address.

### Verify a user's email

To verify a user's email, send a POST request to /verify with the email and verification code as form data:

```python
POST /verify HTTP/1.1
Content-Type: application/x-www-form-urlencoded

email=johndoe@example.com&code=1234
```
if the email and code are valid and have not expired, the API will return a success message:

```python
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Email johndoe@example.com authenticated successfully."
}
```
If the email or code are invalid or have expired, the API will return an error message with an appropriate status code.