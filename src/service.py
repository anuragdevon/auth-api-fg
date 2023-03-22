# Imports
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status, Response, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
import os

# Load Environment Variables
load_dotenv()
# load_dotenv(os.environ["ENVIRONMENT"])

from utils import *
from db_helper.db_views import *

# App Intialization
app = FastAPI()

# Enable CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH Decorators BEGIN
# =========================


@app.post("/auth/user/signup")
async def user_signup(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()
        username = inputData["name"]
        password = inputData["password"]
        email = inputData["email"]
        user_avatar_encoded = inputData["avatar"]

        response = ""
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        # Process Function
        # User Data Initialisation
        user_db_data = user_data_init()

        # Default Avatar
        avatar_url = os.environ["DEFAULT_AVATAR_URL"]
        # Upload Avatar
        # if not (user_avatar_encoded == ""):
        #     avatar_name = username + "_" + ".png"
        #     avatarInputData = {
        #         "avatar_name": avatar_name,
        #         "avatar": user_avatar_encoded
        #     }
        #     avatar_url, ErrorData = upload_user_avatar(avatarInputData)

        # Call DB Service to Add User
        addUserInputData = {
            "user_data": {
                "email": email,
                "name": username,
                "password": password,
                "avatar_url": avatar_url,
            }
        }

        addUserInputData["user_data"].update(user_db_data)

        addUserData, ErrorData = add_user(addUserInputData)

        # Check if User is added to DB successfully
        if ErrorData["code"] == status.HTTP_200_OK:
            response = "verfication email sent"
        else:
            response = "signup failed!"

        # Send Outputs
        ResponseData = {"output": response, "error": ErrorData}
        return JSONResponse(ResponseData)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@app.post("/auth/user/login")
async def user_login(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()
        email = inputData["email"]
        password = inputData["password"]

        response = {}
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        # Call DB Service to Login User
        login_data = {"email": email, "password": password}
        login_response, ErrorData = login_user(login_data)

        # Send Outputs
        ResponseData = {"output": login_response, "error": ErrorData}

        return JSONResponse(ResponseData)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@app.post("/auth/user/resend/email")
async def user_resend_email(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()
        email = inputData["email"]

        response = {}
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        response, ErrorData = resend_verfication_email(email)

        # Send Outputs
        ResponseData = {"output": response, "error": ErrorData}

        return JSONResponse(ResponseData)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@app.get("/auth/user/get")
async def user_get(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()

        response = {}
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        # Call DB Service to get user data
        getUserData, ErrorData = get_user(inputData)

        # Send Outputs
        ResponseData = {"output": getUserData, "error": ErrorData}
        return JSONResponse(ResponseData)
    except ValueError as e:
        print("user_get[error]: " + str(e))
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@app.post("/auth/user/update")
async def user_update(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()

        response = {}
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        # Process Function
        updateSuccess = False

        # Call DB service to Update User
        updateUserData, ErrorData = update_user(inputData)

        # Check if DB updated successfully
        if ErrorData["code"] == status.HTTP_200_OK:
            updateSuccess = True

        updateUserData["update_success"] = updateSuccess

        # Send Outputs
        ResponseData = {"output": updateUserData, "error": ErrorData}
        return JSONResponse(ResponseData)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@app.post("/auth/user/password/reset")
async def user_password_reset(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()
        email = inputData["email"]

        response = ""
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        e = User_ResetPassword(email)
        if e is None:
            response = "reset link sent to email!"
        else:
            ErrorData = {"code": status.HTTP_204_NO_CONTENT, "desc": "Invalid User!"}

        # Send Outputs
        ResponseData = {"output": response, "error": ErrorData}

        return JSONResponse(ResponseData)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@app.post("/auth/user/delete")
async def user_delete(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()

        response = {}
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        deleteSuccess = False

        # Process Function
        # Call DB service to Delete User
        deleteUserData, ErrorData = delete_user(inputData)

        # Check if User deleted in DB successfully
        if ErrorData["code"] == status.HTTP_200_OK:
            deleteSuccess = True

        deleteUserData["delete_success"] = deleteSuccess

        # Send Outputs
        ResponseData = {"output": deleteUserData, "error": ErrorData}
        return JSONResponse(ResponseData)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


@app.post("/auth/user/logout")
async def user_logout(inputs: Request):
    try:
        # Load Inputs
        inputData = await inputs.json()

        response = {}
        ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

        # Process Function
        # Call DB Service to Logout
        try:
            logoutUserData, ErrorData = logout_user(inputData)
            response = logoutUserData

        except Exception as e:
            generate_error(e)
            ErrorData = {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "desc": "Unable to logout user!",
            }

        # Send Outputs
        ResponseData = {"output": response, "error": ErrorData}
        return JSONResponse(ResponseData)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


# =========================
# AUTH Decorators END


# Driver Code
if __name__ == "__main__":
    uvicorn.run(
        "service:app",
        host=os.getenv("host"),
        port=int(os.getenv("port")),
        log_level="info",
        reload=True,
    )
