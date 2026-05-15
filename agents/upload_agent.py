from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video():

    # Authentication
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        SCOPES
    )

    credentials = flow.run_local_server(port=0)

    # Build YouTube service
    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    # Upload request
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "AI Nature Video",
                "description": "Created using Agentic AI Automation",
                "tags": ["AI", "Nature", "Automation"]
            },
            "status": {
                "privacyStatus": "private"
            }
        },

        media_body=MediaFileUpload(
            "videos/final_video.mp4"
        )
    )

    # Execute upload
    response = request.execute()

    print("\nUpload Successful!")
    print("Video ID:", response["id"])