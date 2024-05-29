import os
import sys
import argparse
from logger import logging
from exception import CustomException
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

def getdrive(folderid:str):
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    credentials_file = "desktop_credentials.json"
    app_flow = InstalledAppFlow.from_client_secrets_file(
      credentials_file, scopes=SCOPES
  )
    credentials = app_flow.run_local_server(port = 0)
    drive_service = build("drive", "v3", credentials=credentials)
    folder_id = folderid
    results = (
      drive_service.files()
      .list(
          q=f"'{folder_id}' in parents and (mimeType = 'application/pdf' or mimeType = 'text/plain')",
          fields="files(id, name)",
      )
      .execute()
  )
    logging.info("Files retrieved")
    files = results.get("files", [])
    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        response = drive_service.files().get_media(fileId=file_id).execute()
        os.makedirs("./data", exist_ok = True)
        with open(f"./data/{file_name}", "wb") as pdf_file:
            pdf_file.write(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="folder id")
    parser.add_argument(
        "--folderid", type=str, help="drive folder id", required=True
    )
    args = parser.parse_args()
    try:
      getdrive(args.folderid)
    except Exception as e:
      logging.info("Error in accessing drive")
      raise CustomException(e, sys)
