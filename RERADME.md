# 🚀 YouTube Playlist Transcript Fetcher

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=yellow)](https://www.python.org/)
[![License](https://img.shields.io/github/license/nobody55555/yt-transcript-fetcher?style=flat-square)](https://github.com/nobody55555/yt-transcript-fetcher/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/nobody55555/yt-transcript-fetcher?style=social)](https://github.com/nobody55555/yt-transcript-fetcher)

**Bulk-fetch transcripts for ALL videos in public YouTube playlists** using official APIs. Production-grade CLI tool for researchers, students & analysts.

## ✨ **Key Features**
- `https://youtube.com/playlist?list=PL...` → JSON transcripts for all videos
- ⚡ **Concurrent API calls** (5-10x faster)
- 📊 **Summary report** + individual files
- 🛡 Production error handling & retries
- 🔧 Fully configurable CLI

## 🎯 **2-Minute Setup**

```bash
git clone https://github.com/nobody55555/yt-transcript-fetcher
cd yt-transcript-fetcher
pip install -r requirements.txt

# Add FREE API keys
cp .env.example .env
# Edit .env → Add keys below ↓
```

### 💰 **Free API Keys (5 min setup)**
| Service | Free Tier | Get Key |
|---------|-----------|---------|
| [YouTube Data API v3](https://console.developers.google.com/apis/library/youtube.googleapis.com) | 10k req/day (~200 playlists) | [Create](https://console.cloud.google.com/) |
| [TranscriptAPI](https://transcriptapi.com/) | 100 req/month | [Sign Up](https://dashboard.transcriptapi.com/) |

## ▶ **Usage Examples**

```bash
# Single playlist (default: 50 videos max)
python yt_transcript_fetcher.py "https://www.youtube.com/playlist?list=PLabc123"

# Multiple playlists → separate folders
python yt_transcript_fetcher.py url1 url2 -o ./my-transcripts

# Custom limits
python yt_transcript_fetcher.py url --max-videos 100 --workers 10

# API quota friendly
python yt_transcript_fetcher.py url --single-threaded
```

## 📁 **Output Structure**
```
transcripts/PLabc123/
├── video1_title.json     # Full transcript
├── video2_title.json
├── ...
└── summary.json          # 📊 95% success, 42/50 videos
```

**Sample `summary.json`**:
```json
{
  "total_videos": 50,
  "successful_transcripts": 42,
  "success_rate": "84.0%",
  "playlist_id": "PLabc123"
}
```

## 🏗 **Tech Stack**
```
Python 3.8+  •  requests  •  ThreadPoolExecutor  •  dataclasses
YouTube Data API v3  •  TranscriptAPI.com
argparse CLI  •  JSON output  •  MIT License
```

## 🔮 **Roadmap**
- [ ] Google OAuth (private playlists/watch history)
- [ ] SRT/VTT/CSV export formats
- [ ] Web dashboard

## 🙌 **Portfolio Credits**
**Built by [nobody55555](https://github.com/nobody55555)**  
*Open source automation for researchers & developers*

---

[![Made with HackerAI](https://img.shields.io/badge/Made%20with-HackerAI-000000?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTAgMjBjMCAxMS40IDkuMiAyMCAyMCAyMHMxOS40LTguNiAyMC0yMFMzMS40IDEwIDIwIDEwUzEwIDguNiAxMCAyMFoiIGZpbGw9IiM0RDQ1RjIiLz48L3N2Zz4=)](https://hackerai.co/)
