# Imports
from google.auth import credentials
from google.cloud import storage
import os

# Main Vars
STORAGE_CLIENT = {"spirit_profiles": None, "terraingen": None}

# Main Functions
def StorageInit():
    global STORAGE_CLIENT
    for key in STORAGE_CLIENT:
        STORAGE_CLIENT[key] = storage.Client().bucket(key)  # CHANGE TO NEEDED BUCKET


# Generic Functions
def UploadFileToStorage(storagelocation, local_filepath, key):
    STORAGE_CLIENT[key].blob(storagelocation).upload_from_filename(local_filepath)


def DownloadFileFromStorage(storagepath, local_filepath, key):
    STORAGE_CLIENT[key].blob(storagepath).download_to_filename(local_filepath)


def DownloadAllFilesInFolderStorage(storageLoc, saveLoc, key):
    all_files = STORAGE_CLIENT[key].list_blobs()
    for f in all_files:
        if f.name.startswith(storageLoc) and not f.name.lstrip(storageLoc).strip() == "":
            print("Downloading " + f.name)
            STORAGE_CLIENT[key].blob(f.name).download_to_filename(os.path.join(os.getcwd(), saveLoc + f.name))


def CheckFileInStorage(storagelocation, key):
    return STORAGE_CLIENT[key].blob(storagelocation).exists()


def GetFileURLInStorage(storagelocation, key):
    fileBlob = STORAGE_CLIENT[key].blob(storagelocation)
    fileBlob.make_public()
    return fileBlob.public_url
