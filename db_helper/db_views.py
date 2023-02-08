# Imports
from fastapi import status
import base64

from .utils_auth import *

# - Auth DB_VIEWS ------------------------------------------------------------------------------------------------------

# Main Vars
AUTH_USERPROFILES_BLOB = ""
AUTH_SAVEPATH = ""
GCP_STORAGE = "spirit_profiles"

# User Commands
def add_user(inputData):
    UserData = inputData["user_data"]

    response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    # Process Function
    try:
        # Add
        user_data = {
            "name": UserData["name"],
            "email": UserData["email"],
            "password": UserData["password"],
            "photo_url": UserData["avatar_url"]
        }
        User_Add(**user_data)
            
    except Exception as e:
        generate_error(e)
        # Classification of errors
        if str(e).startswith("Malformed email"):
            ErrorData = {"code": status.HTTP_406_NOT_ACCEPTABLE, "desc": "Invalid Email!"}
        elif str(e).startswith("Invalid password string"):
            ErrorData = {"code": status.HTTP_406_NOT_ACCEPTABLE, "desc": "Invalid Password"}
        elif str(e).endswith("(EMAIL_EXISTS)."):
            ErrorData = {"code": status.HTTP_406_NOT_ACCEPTABLE, "desc": "User Already Exists!"}
        else:
            ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Internal Server Error"}

    # Add User DB Data
    if ErrorData["code"] == status.HTTP_200_OK:
        try:
            # Add Firestore fields
            user_db_data = {}
            for k in FIRESTORE_FIELDS_INIT.keys():
                if k in UserData.keys():
                    user_db_data[k] = UserData[k]
            user_data = User_GetWithEmail(UserData["email"])
            UserDB_Add(user_data.uid, user_db_data)
            # Add Firestore Subcollections
            for k in FIRESTORE_SUBCOLLECTIONS_INIT.keys():
                if k in UserData.keys():
                    UserDB_AddSubcollection(user_data.uid, k, UserData[k])
        except Exception as e:
            generate_error(e)
            ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Internal Server Error"}

    # Send Verify Email
    if ErrorData["code"] == status.HTTP_200_OK:
        try:
            User_VerifyEmail(UserData["email"])
        except Exception as e:
            generate_error(e)
            ErrorData = {"code": status.HTTP_503_SERVICE_UNAVAILABLE, "desc": "Unable to send verification email!"}

    # TODO: ROLLBACK WHEN ERROR HAPPENS
    if not (ErrorData["code"] == status.HTTP_200_OK):
        pass
    # get_session().rollback()
    # TODO: ROLLBACK WHEN ERROR HAPPENS
    return response, ErrorData


def login_user(inputData):
    email = inputData["email"]
    password = inputData["password"]

    response = {
        "id_token": "",
        "refresh_token": ""
    }
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    # Process Function
    login_data = None
    id_token = ""
    refresh_token = ""
    try:
        # Check if email verified
        user_data = User_GetWithEmail(email)
        print(user_data)
        if user_data.email_verified:
            # Login
            login_data = User_Login(email, password)
            if "error" in login_data.keys():
                # If password is wrong or multiple failed attemps
                if login_data["error"]["message"] == "INVALID_PASSWORD":
                    ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Invalid Password!"}
                else: ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Unable to login!"}
                generate_error(login_data)
            else:
                id_token = login_data["idToken"]
                refresh_token = login_data["refreshToken"]
                response = {
                    "id_token": id_token,
                    "refresh_token": refresh_token
                }
        else:
            ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Email not verified!"}
                
    except Exception as e:
        if str(e).startswith("No user record found"):
            ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Invalid Email!"}
        elif login_data is None:
            ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Invalid Email!"}
        generate_error(login_data)
        print("Exception:")
        generate_error(e)

    return response, ErrorData

def resend_verfication_email(email):
    response = ""
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}
    
    try:
        # Process Function
        # Check if email verified
        user_data = User_GetWithEmail(email)
        print(user_data)
        if user_data.email_verified:
            response = "email already verified!"
        else:
            # Send Verify Email
            try:
                User_VerifyEmail(email)
                response = "verification email sent!"
            except Exception as e:
                generate_error(e)
                ErrorData = {"code": status.HTTP_503_SERVICE_UNAVAILABLE, "desc": "Unable to send verification email!"}
                
    except Exception as e:
        generate_error(e)
        ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Invalid User!"}

    return response, ErrorData

def get_user(inputData):

    id_token = inputData["id_token"]
    refresh_token = inputData["refresh_token"]

    response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    UserData = {}
    
    # Process Function
    # Get User Auth Data
    decoded_data, id_token, e = User_UpdateTokens(id_token, refresh_token)
    if e is not None:
        generate_error(e)
        ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Unable to validate user!"}
        id_token = ""
        refresh_token = ""
    
    else:
        UserData = {
            "user_id": decoded_data["uid"],
            "name": decoded_data["name"],
            "email": decoded_data["email"],
            "avatar_url": decoded_data["picture"]
        }

        UserID = decoded_data["uid"]

        # Get User DB Data
        try:
            user_db_data = UserDB_Get(UserID).to_dict()
            UserData["following"] = user_db_data["following"]
            UserData["follower"] = user_db_data["follower"]
            UserData["redemption_cards"] = user_db_data["redemption_cards"]
            UserData["reward_cards"] = user_db_data["reward_cards"]

        except Exception as e:
            generate_error(e)
            ErrorData = {"code": status.HTTP_204_NO_CONTENT, "desc": "Unable to get user info!"}

    response["id_token"] = id_token
    response["refresh_token"] = refresh_token
    response["response"] = UserData

    return response, ErrorData

def get_user_other(inputData):

    id_token = inputData["id_token"]
    refresh_token = inputData["refresh_token"]
    UserID = inputData["user_id"]

    response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    # Process Function
    # Get User Auth Data
    decoded_data, id_token, e = User_UpdateTokens(id_token, refresh_token)
    if e is not None:
        generate_error(e)
        ErrorData = {"code": status.HTTP_401_UNAUTHORIZED, "desc": "Unable to validate user!"}
        id_token = ""
        refresh_token = ""
    
    else:
        user_data = User_Get(UserID)
        response = {
            "response": {
                "user_id": user_data.uid,
                "name":user_data.display_name,
                "email": user_data.email,
                "avatar_url": user_data.photo_url
            }
        }
        # Get User DB Data
        try:
            user_db_data = UserDB_Get(UserID).to_dict()
            print(user_db_data)
            response["response"]["followers_count"] = len(user_db_data["follower"])
            response["response"]["following_count"] = len(user_db_data["following"])
        except Exception as e:
            generate_error(e)
            ErrorData = {"code": status.HTTP_204_NO_CONTENT, "desc": "Unable to get user data!"}

    response["id_token"] = id_token
    response["refresh_token"] = refresh_token

    return response, ErrorData


def update_user(inputData):
    # Load Inputs
    id_token = inputData["id_token"]
    refresh_token = inputData["refresh_token"]
    UserData = inputData["user_data"]

    # response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    # Process Function
    # Update User Auth Data
    decoded_data, id_token, e = User_UpdateTokens(id_token, refresh_token)
    if e is not None:
        generate_error(e)
        ErrorData = {"code": status.HTTP_403_FORBIDDEN, "desc": "Unable to validate user!"}

    if ErrorData["code"] == status.HTTP_200_OK:
        try:
            uid = decoded_data["uid"]
            user_auth_data = {
                "name": UserData["name"] if "name" in UserData.keys() else None,
                "email": UserData["email"] if "email" in UserData.keys() else None,
                "photo_url": UserData["avatar_url"] if "avatar_url" in UserData.keys() else None
            }
            User_Update(uid, **user_auth_data)
        except Exception as e:
            print("update_user[Error]: ", str(e))
            ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Unable to update!"}

    response = {
        "id_token": id_token,
        "refresh_token": refresh_token
    }
    return response, ErrorData


def delete_user(inputData):
    # Load Inputs
    id_token = inputData["id_token"]
    refresh_token = inputData["refresh_token"]

    response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    # Process Function
    # User Auth Delete
    decoded_data, id_token, e = User_UpdateTokens(id_token, refresh_token)
    if e is not None:
        print("delete_user:[Error]: ", str(e))
        ErrorData = {"code": status.HTTP_403_FORBIDDEN, "desc": "Unable to validate user!"}

    if ErrorData["code"] == status.HTTP_200_OK:
        try:
            uid = decoded_data["uid"]
            # Delete
            User_Delete(uid)
        except Exception as e:
            print("delete_user:[Error]: ", str(e))
            ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Unable to delete user!"}

    # User DB Delete
    if ErrorData["code"] == status.HTTP_200_OK:
        try:
            UserDB_Delete(decoded_data["uid"])
        except Exception as e:
            print("delete_user:[Error]: ", str(e))
            ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Unable to delete completely!"}

    response = {
        "id_token": "",
        "refresh_token": ""
    }
    return response, ErrorData


def logout_user(inputData):
    # Load Inputs
    id_token = inputData["id_token"]
    refresh_token = inputData["refresh_token"]

    response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    # Process Function
    decoded_data, id_token, e = User_UpdateTokens(id_token, refresh_token)
    if e is not None:
        generate_error(e)
        ErrorData = {"code": status.HTTP_403_FORBIDDEN, "desc": "Unable to validate user!"}

    if ErrorData["code"] == status.HTTP_200_OK:
        try:
            uid = decoded_data["uid"]
            # Logout by Revoking all current refresh tokens
            User_RevokeRefreshTokens(uid)
        except Exception as e:
            generate_error(e)
            ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Unable to logout user!"}

    response ={
        "id_token": "",
        "refresh_token": ""
    }
    return response, ErrorData


def upload_user_avatar(inputs):
    # Load Inputs
    inputData = inputs.data
    avatar_name = inputData["avatar_name"]
    AvatarEncodedData = inputData["avatar"]

    response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    # Process Function
    try:
        storagePath = AUTH_USERPROFILES_BLOB + avatar_name
        localPath = AUTH_SAVEPATH + avatar_name

        # Decode avatar
        img_bytes = base64.b64decode(AvatarEncodedData.encode("utf-8"))
        open(localPath, "wb").write(img_bytes)

        # Upload the file
        UploadFileToStorage(storagePath, localPath, GCP_STORAGE)
        fileLink = GetFileURLInStorage(storagePath, GCP_STORAGE)
        response = fileLink

        # Delete the local file
        os.remove(localPath)
    except Exception as e:
        print("upload_user_avatar[Error]:", str(e))
        ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Avatar upload failed!"}

    return response, ErrorData


def user_data_init():
    user_db_data = {}
    # Init Firestore Fields
    for k in FIRESTORE_FIELDS_INIT.keys():
        if FIRESTORE_FIELDS_INIT[k] is not None:
            user_db_data[k] = FIRESTORE_FIELDS_INIT[k]
    # Init Firestore Subcollections
    for k in FIRESTORE_SUBCOLLECTIONS_INIT.keys():
        if FIRESTORE_SUBCOLLECTIONS_INIT[k] is not None:
            user_db_data[k] = FIRESTORE_SUBCOLLECTIONS_INIT[k]
    return user_db_data


def update_following(inputData):
    # Load Inputs
    id_token = inputData["id_token"]
    refresh_token = inputData["refresh_token"]
    following_user_id = inputData["user_id_following"]
    following_update = inputData["following"]
    # add=True 

    response = {}
    ErrorData = {"code": status.HTTP_200_OK, "desc": "No Error"}

    decoded_data, id_token, e = User_UpdateTokens(id_token, refresh_token)
    if e is not None:
        print("update_following:[Error]: ", str(e))
        ErrorData = {"code": status.HTTP_403_FORBIDDEN, "desc": "Unable to validate user!"}

    if ErrorData["code"] == status.HTTP_200_OK:
        try:
            global FIRESTORE_FIELDS
            UserID = decoded_data["uid"]

            # Get Following UserID
            UserID_Following = following_user_id

            # Update Following and Follower Data in Firestore
            # Update Following for Current User
            UserDB_UpdateArray(UserID, "following", UserID_Following, following_update)
            # Update Follower for Other User
            UserDB_UpdateArray(UserID_Following, "follower", UserID, following_update)

        except Exception as e:
            print("update_following:[Error]: ", str(e))
            ErrorData = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "desc": "Cannot update follow!"}

    response = {
        "id_token": id_token,
        "refresh_token": refresh_token
    }
    return response, ErrorData

# - Auth DB_VIEWS------------------------------------------------------------------------------------------------------
