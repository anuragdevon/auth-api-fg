# Imports
import os
from .verfication_page import *
import sib_api_v3_sdk

# Main Functions
def VerificationEmail_Send(verify_email, verify_link):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("SENDINBLUE_API_KEY")
    print(os.getenv("SENDINBLUE_API_KEY"))

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = "Contact From Auth Module"
    html_content = html_design(verify_link)
    sender = {"name":"Auth Module","email":"anuragdevon@gmail.com"}
    to = [{"email":verify_email,"name":"User"}]
    headers = {"Some-Custom-Name":"unique-id-1234"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, headers=headers, html_content=html_content, sender=sender, subject=subject)

    api_instance.send_transac_email(send_smtp_email)