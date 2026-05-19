from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video():

    # =========================
    # READ SEO FILE
    # =========================

    with open("seo.txt", "r", encoding="utf-8") as file:
        seo_data = file.read()

    # Default values
    title = "AI Generated Video"
    description = "Created using AI"
    tags = ["AI"]

    # =========================
    # EXTRACT TITLE
    # =========================

    if "TITLE:" in seo_data:
        title = seo_data.split("TITLE:")[1].split("\n")[0].strip()

    # =========================
    # EXTRACT DESCRIPTION
    # =========================

    if "DESCRIPTION:" in seo_data:
        description = seo_data.split("DESCRIPTION:")[1].split("\n")[0].strip()

    # =========================
    # EXTRACT TAGS
    # =========================

    if "TAGS:" in seo_data:

        tags_text = seo_data.split("TAGS:")[1].split("\n")[0]

        tags = [tag.strip() for tag in tags_text.split(",")]

    # =========================
    # AUTHENTICATION
    # =========================

    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        SCOPES
    )

    credentials = flow.run_local_server(port=0)

    # =========================
    # BUILD YOUTUBE SERVICE
    # =========================

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    # =========================
    # VIDEO UPLOAD
    # =========================

    request = youtube.videos().insert(
        part="snippet,status",

        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"
            },

            "status": {
                "privacyStatus": "private"
            }
        },

        media_body=MediaFileUpload(
            "videos/final_video.mp4"
        )
    )

    response = request.execute()

    video_id = response["id"]

    print("\nVideo Uploaded Successfully!")
    print("Video ID:", video_id)

    # # =========================
    # # THUMBNAIL UPLOAD
    # # =========================

    # youtube.thumbnails().set(
    #     videoId=video_id,
    #     media_body=MediaFileUpload(
    #         "scenes/thumbnail.png"
    #     )
    # ).execute()

    # print("\nThumbnail Uploaded Successfully!")