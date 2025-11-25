<div align="center">

# 🎥 GoPro Plus Downloader 2

**Break free from the 25-file download limit**

A powerful CLI tool to bulk download your entire GoPro Plus media library without restrictions.

[![Docker Hub](https://img.shields.io/docker/pulls/maxrodrigo/gopro?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/r/maxrodrigo/gopro)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/maxrodrigo/gopro-plus?style=flat-square)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start-docker) • [Installation](#-local-installation) • [Troubleshooting](#-troubleshooting)

</div>

---

## 💡 Why This Tool?

This tool lets you download your entire media library in bulk, making it easy to:

- 📤 Migrate to Google Drive, Dropbox, or any cloud storage
- 💾 Backup to your self-hosted NAS (Synology, TrueNAS, etc.)
- 🎬 Access your full media collection offline
- � Automate regular backups with Docker

## ✨ Features

* 📦 **Bulk Download** - Download all your GoPro Plus media without the 25-file limit
* 🔄 **Idempotent Downloads** - Safely re-run downloads; already downloaded files are automatically skipped
* 🔁 **Automatic Retry** - Network failures are handled with exponential backoff retry logic (restarts from scratch on failure)
* 🐳 **Docker Support** - Run in a containerized environment for easy deployment
* 🖥️ **CLI Interface** - Full command-line control with flexible options

---

## 🚀 Quick Start (Docker)

**Prerequisites:** Get your `AUTH_TOKEN` and `USER_ID` from [Environment Variables](#-environment-variables) section below.

```bash
docker run --name gopro-downloader \
  -e AUTH_TOKEN='<YOUR_TOKEN>' \
  -e USER_ID='<YOUR_USER_ID>' \
  -v /path/to/download:/app/download \
  maxrodrigo/gopro:latest
```

### Docker Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AUTH_TOKEN` | ✅ Yes | - | Authentication token from GoPro Media Library |
| `USER_ID` | ✅ Yes | - | User ID from GoPro Media Library |
| `ACTION` | ❌ No | `download` | Action to execute: `list` or `download` |
| `START_PAGE` | ❌ No | `1` | Starting page number |
| `PAGES` | ❌ No | `1000000` | Number of pages to process |
| `PER_PAGE` | ❌ No | `15` | Items per page |
| `PROGRESS_MODE` | ❌ No | `noline` | Progress display: `inline`, `newline`, or `noline` |

## 🔑 Environment Variables

To set up `AUTH_TOKEN` and `USER_ID`, you need to extract them from your GoPro Plus account.

### Method 1: Browser Console (Easiest) ⚡

1. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/) and **log in**
2. Open your browser's Developer Tools:
   - **Chrome/Firefox/Edge**: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)
   - **Safari**: Enable Developer Menu in Preferences, then press `Cmd+Option+I`
3. Click on the **Console** tab
4. Paste this command and press Enter:

```javascript
console.log('AUTH_TOKEN=' + document.cookie.split('; ').find(row => row.startsWith('gp_access_token=')).split('=')[1] + '\nUSER_ID=' + document.cookie.split('; ').find(row => row.startsWith('gp_user_id=')).split('=')[1]);
```

5. Copy the output - it will show both values ready to use! 🎉

### Method 2: Manual Extraction

1. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/) and **log in**
2. Open Developer Tools (`F12` or `Ctrl+Shift+I` / `Cmd+Option+I`)
3. Go to the **Network** tab
4. In the filter field, type: `user`
5. Refresh the page if needed
6. Click on any request and find the **Cookies** tab
7. Look for these cookies:
   - `gp_access_token` - starts with `eyJhbGc...` → Copy to `AUTH_TOKEN`
   - `gp_user_id` - the user ID → Copy to `USER_ID`

For Docker:
```bash
docker run -e AUTH_TOKEN=<gopro-auth-token> -e USER_ID=<gopro-user-id> maxrodrigo/gopro:latest
```

For Linux/macOS:
```bash
export AUTH_TOKEN="<gibberish_string_here>"
export USER_ID="<user-id>"
```

For Windows Command Prompt:
```cmd
set AUTH_TOKEN="<gibberish_string_here>"
set USER_ID="<user-id>"
```

For Windows PowerShell:
```sh
$env:AUTH_TOKEN="<gibberish_string_here>"
$env:USER_ID="<user-id>"
```

Once the `AUTH_TOKEN` and `USER_ID` are set, you can run the application without passing them explicitly each time.

---

## 🔧 Troubleshooting

### Docker logs
```bash
docker logs gopro-downloader
```

### Common Issues

* **Authentication failed**: Your `AUTH_TOKEN` or `USER_ID` may have expired. Re-authenticate and update your environment variables.
* **Download stuck**: The script validates existing files before downloading. For large ZIP files, this may take a moment.
* **File already exists**: The script is idempotent - it will skip files that are already fully downloaded.

### Download Failures and Retry Behavior

**Important**: When a download fails and retries, it **restarts from the beginning**. ZIP files are dynamically generated by the GoPro API and cannot be resumed without corruption.

**If you experience repeated download failures:**

1. **Reduce items per page** - Smaller ZIP files are more reliable and faster to download
   ```bash
   # Instead of default 30 items per page
   ./gopro --per-page 10
   
   # For very unstable connections, try even smaller batches
   ./gopro --per-page 5
   ```

2. **Increase retry attempts** - Give the script more chances to complete the download
   ```bash
   ./gopro --max-retries 10
   ```

3. **Process fewer pages at a time** - Download in smaller batches
   ```bash
   # Download pages 1-5
   ./gopro --start-page 1 --pages 5
   
   # Then continue with pages 6-10
   ./gopro --start-page 6 --pages 5
   ```

**Recommended strategy for unreliable connections:**
```bash
./gopro --per-page 10 --max-retries 10 --progress-mode newline
```

This creates smaller, more manageable ZIP files that are less likely to fail and faster to retry if they do.

---

## 🤝 Contributing

Interested in contributing? Check out [CONTRIBUTING.md](CONTRIBUTING.md) for:

- 💻 Local development setup
- 🐳 Docker development workflow
- 📝 Coding guidelines
- 🔄 Contribution workflow

## 📄 License

This project is open source. Check the [LICENSE](LICENSE) file for details.

<div align="center">

If this tool helped you, consider giving it a ⭐ on GitHub!

</div>
