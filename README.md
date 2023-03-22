# Authit-Python: Fast and Secure Authentication with Python, FastAPI, and Firebase

Authit-Python is a Python module for implementing user authentication in web and mobile apps. It's built on top of the FastAPI framework and uses Firebase for authentication and database management. With Authit-Python, you can quickly and easily add secure user authentication to your web or mobile app.

## Features

- User signup with name, email, password, and avatar (optional)
- User login with email and password
- Resend verification email
- Get user data
- Update user data

## Requirements

- Docker - Running
- Bash/Postman - Testing

## Installation

1. Clone the repository to your local machine:

```
git clone https://github.com/your_username/authit-python.git
```


2. Navigate to the project directory:


```
cd authit-python
```

3. Add your Firebase API key and project ID to a .env file in the root directory of the project

```
FIREBASE_API_KEY=<your_firebase_api_key>
FIREBASE_PROJECT_ID=<your_firebase_project_id>
```

3. Setup the Docker container:

```
docker build -t authit-python .
docker run -p 8000:8000 authit-python
```



The application should now be accessible at http://localhost:8000.

## API Documentation

The API documentation is available at http://localhost:8000/swagger/ or http://localhost:8000/redoc/ when the development server is running.


## Usage
Authit-python provides a RESTful API that can be tested with scripts or Postman.

### Signup
To sign up a new user, make a POST request to the /auth/user/signup endpoint with the following JSON payload:

```
{
    "name": "<user_name>",
    "email": "<user_email>",
    "password": "<user_password>",
    "avatar": "<base64_encoded_avatar>" (optional)
}
```

### Login
To log in a user, make a POST request to the /auth/user/login endpoint with the following JSON payload:

```
{
    "email": "<user_email>",
    "password": "<user_password>"
}
```

### Resend Verification Email
To resend a verification email to a user, make a POST request to the /auth/user/resend/email endpoint with the following JSON payload:

```
{
    "email": "<user_email>"
}
```

### Get User Data
To get user data, make a GET request to the /auth/user/get endpoint with the following JSON payload:

```
{
    "id_token": "<id_token>",
    "refresh_token": "<refresh_token>"
}
```

### Update User Data
To update user data, make a POST request to the /auth/user/update endpoint with the following JSON payload:

```
{
    "id_token": "<id_token>",
    "refresh_token": "<refresh_token>"
    "new_name": "<new_user_name>",
    "new_avatar": "<base64_encoded_new_avatar>" (optional)
}
```

### Signup
To sign up a new user, make a POST request to the /auth/user/signup endpoint with the following JSON payload:

```
{
    "name": "<user_name>",
    "email": "<user_email>",
    "password": "<user_password>",
    "avatar": "<base64_encoded_avatar>" (optional)
}
```

### Signup
To sign up a new user, make a POST request to the /auth/user/signup endpoint with the following JSON payload:

```
{
    "name": "<user_name>",
    "email": "<user_email>",
    "password": "<user_password>",
    "avatar": "<base64_encoded_avatar>" (optional)
}
```

## Contributing

Contributions to the project are welcome. Before making any changes, please create an issue to discuss the proposed changes.

To set up a development environment, follow the installation instructions above and create a new branch for your changes:

```
git checkout -b my-feature-branch
```


After making your changes, run the tests to ensure that everything is working correctly:

```
python src/test/main.py
```


Finally, submit a pull request to merge your changes into the main branch.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
