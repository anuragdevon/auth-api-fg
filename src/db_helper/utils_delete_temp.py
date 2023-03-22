# # Import
# import os
# from firebase_admin import auth
# import firebase_admin
# # result = auth.get_users()

# # print('Successfully fetched user data:')
# # for user in result.users:
# #     print(user.uid)

# # print('Unable to find users corresponding to these identifiers:')
# # for uid in result.not_found:
# #     print(uid)

# # firebase_admin.auth.list_users(page_token=None, max_results=1000, app=None)

# FIREBASE_APP = None
# # Main Functions
# def FirebaseInit():
#     global FIREBASE_APP
#     global FIREBASE_DB

#     CRED = firebase_admin.credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS_AUTH'])
#     FIREBASE_APP = firebase_admin.initialize_app(credential=CRED)
#     # FIREBASE_DB = firestore.client(app=FIREBASE_APP)

# FirebaseInit()

# def get_all_users():
#     all_users = auth.list_users(app=FIREBASE_APP).users
#     all_uids = [u.uid for u in all_users]
#     return all_uids

# # print(get_all_users())
