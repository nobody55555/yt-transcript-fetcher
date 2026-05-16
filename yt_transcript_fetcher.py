import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Configuration
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
TRANSCRIPT_API_KEY = os.getenv('TRANSCRIPT_API_KEY')

if not YOUTUBE_API_KEY or not TRANSCRIPT_API_KEY:
    raise ValueError("Missing API keys in .env file")

BASE_TRANSCRIPT_URL = "https://transcriptapi.com/api/v2/youtube/transcript"

HEADERS = {
    "Authorization": f"Bearer {TRANSCRIPT_API_KEY}"
}


def get_playlist_videos(playlist_id: str, max_results: int = 100) -> List[Dict]:
    """Fetch all videos from a YouTube playlist using pagination."""
    videos = []
    page_token = None
    url = "https://www.googleapis.com/youtube/v3/playlistItems"

    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": min(50, max_results - len(videos)),
            "key": YOUTUBE_API_KEY,
        }
        if page_token:
            params["pageToken"] = page_token

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error fetching playlist: {response.text}")
            break

        data = response.json()
        videos.extend(data.get("items", []))

        page_token = data.get("nextPageToken")
        if not page_token or len(videos) >= max_results:
            break

        time.sleep(0.1)  # Be respectful

    return videos


def extract_video_info(video_item: Dict) -> Dict:
    """Extract relevant info from playlist item."""
    snippet = video_item["snippet"]
    content_details = video_item["contentDetails"]
    return {
        "video_id": content_details["videoId"],
        "title": snippet["title"],
        "channel_title": snippet["channelTitle"],
        "published_at": snippet["publishedAt"],
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        "playlist_id": video_item["snippet"]["playlistId"],
    }


def fetch_transcript(video_url: str, video_info: Dict) -> Optional[Dict]:
    """Fetch transcript using TranscriptAPI.com."""
    try:
        params = {
            "video_url": video_url,
            "send_metadata": "true",
        }
        response = requests.get(BASE_TRANSCRIPT_URL, params=params, headers=HEADERS, timeout=30)

        if response.status_code == 200:
            data = response.json()
            transcript_data = {
                **video_info,
                "transcript": data.get("transcript", []),
                "language": data.get("language"),
                "duration": data.get("duration"),
                "fetched_at": datetime.utcnow().isoformat(),
            }
            return transcript_data
        else:
            print(f"Transcript error for {video_url}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception fetching transcript for {video_url}: {e}")
        return None


def save_transcript(data: Dict, output_dir: Path):
    """Save transcript to JSON file."""
    video_id = data["video_id"]
    file_path = output_dir / f"{video_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved: {file_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube playlist transcripts")
    parser.add_argument("playlist_url", nargs="+", help="One or more YouTube playlist URLs or IDs")
    parser.add_argument("--max", type=int, default=500, help="Max videos to process (default: 500)")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent workers (default: 10)")
    parser.add_argument("--output", type=str, default="transcripts", help="Output directory")
    parser.add_argument("--quota-friendly", action="store_true", help="Slower mode with more delays")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    all_videos = []
    for url in args.playlist_url:
        # Extract playlist ID
        if "list=" in url:
            playlist_id = url.split("list=")[-1].split("&")[0]
        else:
            playlist_id = url  # assume it's already an ID

        print(f"Fetching videos from playlist: {playlist_id}")
        videos = get_playlist_videos(playlist_id, args.max)
        print(f"Found {len(videos)} videos")
        all_videos.extend(videos)

    # Process with concurrency
    results = []
    failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_video = {}
        for video_item in all_videos:
            info = extract_video_info(video_item)
            video_url = f"https://youtube.com/watch?v={info['video_id']}"
            future = executor.submit(fetch_transcript, video_url, info)
            future_to_video[future] = info['video_id']

        for future in as_completed(future_to_video):
            vid_id = future_to_video[future]
            try:
                data = future.result()
                if data:
                    save_transcript(data, output_dir)
                    results.append(data)
                else:
                    failed += 1
            except Exception as e:
                print(f"Error processing {vid_id}: {e}")
                failed += 1
            if args.quota_friendly:
                time.sleep(1)

    # Summary
    summary = {
        "total_videos": len(all_videos),
        "successful": len(results),
        "failed": failed,
        "output_dir": str(output_dir),
        "fetched_at": datetime.utcnow().isoformat(),
        "playlist_urls": args.playlist_url,
    }

    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*50)
    print("SUMMARY")
    print(f"Total videos: {summary['total_videos']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Output: {output_dir}")
    print("="*50)


if __name__ == "__main__":
    main()
