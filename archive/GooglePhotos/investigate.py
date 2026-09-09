from google.oauth2 import service_account
from googleapiclient.discovery import build

# Authenticate with your credentials
service_account_file = "credentials.json"
scopes = ["https://www.googleapis.com/auth/photoslibrary.readonly"]

credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=scopes)

service = build("photoslibrary", "v1", credentials=credentials)

# List media items
results = service.mediaItems().list(pageSize=100).execute()
items = results.get("mediaItems", [])
print("Number of photos fetched:", len(items))
