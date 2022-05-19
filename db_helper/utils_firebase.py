# Imports
import firebase_admin
import os
import json
import requests
from firebase_admin import auth, firestore

from .utils_email import *

# Main Vars
FIREBASE_APP = None
FIREBASE_DB = None

CollectionName_Users = "users"

FIRESTORE_FIELDS_INIT = {
    "level": 0,
    "exp": 0,
    "credits": 100,
    "cash": 0.0,
    "follower": [],
    "following": [],
    "redemption_cards": {},
    "reward_cards": {}
}
FIRESTORE_SUBCOLLECTIONS_INIT = {
    "redeem_history": {},
    "activity": {},
    "notifications": {}
}

# Main Functions
def FirebaseInit():
    global FIREBASE_APP
    global FIREBASE_DB

    CRED = firebase_admin.credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS_AUTH'])
    FIREBASE_APP = firebase_admin.initialize_app(credential=CRED)
    FIREBASE_DB = firestore.client(app=FIREBASE_APP)

# User DB Functions
def UserDB_Add(uid, user_data):
    global FIREBASE_DB
    return FIREBASE_DB.collection(CollectionName_Users).document(uid).create(user_data)

def UserDB_Delete(uid):
    global FIREBASE_DB
    return FIREBASE_DB.collection(CollectionName_Users).document(uid).delete()

def UserDB_Get(uid):
    global FIREBASE_DB
    return FIREBASE_DB.collection(CollectionName_Users).document(uid).get()

def UserDB_GetField(uid, field):
    global FIREBASE_DB
    return FIREBASE_DB.collection(CollectionName_Users).document(uid).get(field)

def UserDB_Update(uid, user_data):
    global FIREBASE_DB
    return FIREBASE_DB.collection(CollectionName_Users).document(uid).set(user_data, merge=True)

def UserDB_UpdateArray(uid, field, element, add=True):
    global FIREBASE_DB
    ArrayOperation = firestore.ArrayUnion if add else firestore.ArrayRemove
    return FIREBASE_DB.collection(CollectionName_Users).document(uid).update({field: ArrayOperation([element])})

def UserDB_AddSubcollection(uid, subcollection, docs={}):
    global FIREBASE_DB
    for k in docs.keys():
        FIREBASE_DB.collection(CollectionName_Users).document(uid).collection(subcollection).document(k).create(docs[k])
    return None

# User Auth Functions
def User_Add(name, email, password, photo_url):
    global FIREBASE_APP
    return auth.create_user(display_name=name, email=email, email_verified=False, photo_url=photo_url, password=password, app=FIREBASE_APP)

def User_Delete(uid):
    global FIREBASE_APP
    return auth.delete_user(uid=uid, app=FIREBASE_APP)

def User_Get(uid):
    global FIREBASE_APP
    return auth.get_user(uid=uid, app=FIREBASE_APP)

def User_GetWithEmail(email):
    global FIREBASE_APP
    return auth.get_user_by_email(email=email, app=FIREBASE_APP)

def User_Update(uid, name=None, email=None, password=None, photo_url=None):
    global FIREBASE_APP
    params = {}
    if name is not None: params["display_name"] = name
    if email is not None: params["email"] = email
    if password is not None: params["password"] = password
    if photo_url is not None: params["photo_url"] = photo_url
    return auth.update_user(uid=uid, app=FIREBASE_APP, **params)

def User_Login(email, password, return_secure_token=True):
    LOGIN_API_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": return_secure_token
    })

    r = requests.post(LOGIN_API_URL,
        params={"key": os.environ.get("FIREBASE_WEB_API_KEY")},
        data=payload
    )

    return r.json()
# {'error': {'code': 400, 'message': 'INVALID_PASSWORD', 'errors': [{'message': 'INVALID_PASSWORD', 'domain': 'global', 'reason': 'invalid'}]}}"
# "desc": "No user record found for the provided email: zdzzogcimmizuclhaa@sdv.com."
def User_RegenerateIDToken(refresh_token):
    API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")
    REGEN_IDTOKEN_API_URL = f"https://securetoken.googleapis.com/v1/token?key={API_KEY}"
    
    payload = json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    })

    r = requests.post(REGEN_IDTOKEN_API_URL,
        data=payload
    )
    
    id_token = ""
    e = None
    if "id_token" in r.json().keys():
        id_token = r.json()["id_token"]
    else:
        e = "invalid refresh_token"
    return id_token, e

def User_ResetPassword(email):
    API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")
    PASSWORD_RESET_API_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"

    payload = json.dumps({
        "requestType": "PASSWORD_RESET",
        "email": str(email)
    })

    response = requests.post(PASSWORD_RESET_API_URL,
        data=payload
    ).json()
    
    if "error" in response.keys():
        return response["error"]["message"]
    else:
        return None
    # {'error': {'code': 400, 'message': 'EMAIL_NOT_FOUND', 'errors': [{'message': 'EMAIL_NOT_FOUND', 'domain': 'global', 'reason': 'invalid'}]}}
    # {'kind': 'identitytoolkit#GetOobConfirmationCodeResponse', 'email': 'msm19b021@iiitdm.ac.in'}

def User_VerifyEmail(email):
    global FIREBASE_APP
    verify_link = auth.generate_email_verification_link(email)
    # Custom SMTP Server
    VerificationEmail_Send(email, verify_link)

def User_DecodeIDToken(id_token):
    global FIREBASE_APP
    decoded_token = auth.verify_id_token(id_token, app=FIREBASE_APP, check_revoked=True)
    return decoded_token

def User_RevokeRefreshTokens(uid):
    global FIREBASE_APP
    auth.revoke_refresh_tokens(uid, app=FIREBASE_APP)

def User_UpdateTokens(id_token, refresh_token):
    # Check if need to Regenerate ID Token
    decoded_data = {}
    e = None
    try:
        # Decode ID Token
        decoded_data = User_DecodeIDToken(id_token)
    except auth.ExpiredIdTokenError as exp:
        id_token, e_regen = User_RegenerateIDToken(refresh_token)
        if e_regen is None:
            # Decode New ID Token
            decoded_data = User_DecodeIDToken(id_token)
        else:
            e = e_regen
    except Exception as exc:
        e = exc
    return decoded_data, id_token, e

# Verify functions
def User_GetAllUIDs():
    global FIREBASE_APP
    all_users = auth.list_users(app=FIREBASE_APP).users
    all_uids = [u.uid for u in all_users]
    return all_uids

def User_VerfyFirestore():
    global FIREBASE_APP
    global FIREBASE_DB
    all_uids = User_GetAllUIDs()
    deleted_users = []
    conflict_users = []
    uid_conflicts = [True]*len(all_uids)
    # firestore.collections(CollectionName_Users).get()
    docs = FIREBASE_DB.collection(CollectionName_Users).stream()
    for doc in docs:
        # f'{doc.id} => {doc.to_dict()}'
        if doc.id in all_uids:
            uid_conflicts[all_uids.index(doc.id)] = False
        else:
            deleted_users.append(doc.id)

    for uc, u in zip(uid_conflicts, all_uids):
        if uc :
            conflict_users.append(u)
    
    return deleted_users, conflict_users

# Driver Code
FirebaseInit()
