from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaFileUpload


# Ruta al archivo de credenciales
creds = service_account.Credentials.from_service_account_file('../credentials2.json')
drive_service = build('drive', 'v3', credentials=creds)


def upload_to_drive(file_path, folder_id):
    file_metadata = {
        'name': file_path.split('/')[-1],
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='text/csv')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Archivo subido con ID: {uploaded_file.get('id')}")

