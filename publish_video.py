import os, sys
from pathlib import Path
import requests

GRAPH_VERSION = os.getenv("GRAPH_API_VERSION", "v26.0")
PAGE_ID = os.getenv("PAGE_ID")
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VIDEO = Path("output/gopal_bhar.mp4")
CAPTION_FILE = Path("output/caption.txt")

def main():
    if not PAGE_ID or not PAGE_TOKEN:
        print("PAGE_ID or PAGE_ACCESS_TOKEN missing; skipping Facebook upload.")
        return
    if not VIDEO.exists():
        raise FileNotFoundError(f"Video not found: {VIDEO}")
    caption = CAPTION_FILE.read_text(encoding="utf-8") if CAPTION_FILE.exists() else "গোপাল ভাঁড়ের বাংলা কার্টুন"
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/videos"
    with VIDEO.open("rb") as f:
        response = requests.post(
            url,
            data={
                "access_token": PAGE_TOKEN,
                "title": "গোপাল ভাঁড়ের বাংলা কার্টুন",
                "description": caption,
                "published": "true"
            },
            files={"source": ("gopal_bhar.mp4", f, "video/mp4")},
            timeout=600
        )
    try:
        payload = response.json()
    except ValueError:
        raise RuntimeError(f"Meta returned non-JSON response: {response.status_code} {response.text[:500]}")
    if not response.ok or "id" not in payload:
        raise RuntimeError(f"Meta upload failed ({response.status_code}): {payload}")
    print(f"Facebook video accepted. Video ID: {payload['id']}")
    print("Note: acceptance does not guarantee the video has finished processing; check Page publishing status.")

if __name__ == "__main__":
    main()
