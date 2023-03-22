import requests
import json


def user_signup():
    url = "localhost:8080/auth/user/signup"

    payload = json.dumps(
        {
            "email": "wkigykikfgskxtngvz@tmmbt.com",
            "password": "12345678",
            "name": "anuragdevon",
            "avatar": "",
        }
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def user_signin():
    url = "localhost:8080/auth/user/login"

    payload = json.dumps(
        {"email": "wkigykikfgskxtngvz@tmmbt.com", "password": "12345678"}
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def user_update():
    url = "localhost:8080/auth/user/update"

    payload = (
        '{\n    "id_token": '
        ',\n    "refresh_token": '
        ',\n    "user_data": {\n        "name": "kakashi"\n    }\n}'
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def user_logout():
    url = "localhost:8080/auth/user/logout"

    payload = '{\n    "id_token": ' ',\n    "refresh_token": ' "\n}"
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def delete():
    url = "localhost:8080/auth/user/delete"

    payload = '{\n    "id_token": ' ',\n    "refresh_token": ' "\n}"
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def user_password_reset():
    url = "localhost:8080/auth/user/password/reset"

    payload = json.dumps({"email": "wkigykikfgskxtngvz@tmmbt.com"})
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def user_get():
    url = "localhost:8080/auth/user/get"

    payload = '{\n    "id_token": ' ',\n    "refresh_token": ' "\n}"
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
