<div align="center">

# 🎥 GoPro Plus Downloader 2

**Break free from the 25-file download limit**

A powerful CLI tool to bulk download your entire GoPro Plus media library without restrictions.

[![Docker Hub](https://img.shields.io/docker/pulls/maxrodrigo/gopro?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/r/maxrodrigo/gopro)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/maxrodrigo/gopro-plus?style=flat-square)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Contributing](#-contributing) • [Troubleshooting](#-troubleshooting)

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
* �️ **Enhanced Progress Bar** - Real-time download progress with percentage, MB/s speed, and file size display
* 📸 **EXIF Metadata Preservation** - Restores original capture dates and adds camera model/dimensions to JPEG files
* 🔄 **Automatic Retry** - Network failures are handled with exponential backoff retry logic
* �️ **Bulk Deletion** - Delete media from GoPro cloud with safety confirmations and dry-run mode
* 📋 **ID Export** - Export media IDs for backup, deletion, or external processing
* �🐳 **Docker Support** - Run in a containerized environment for easy deployment
* 🖥️ **CLI Interface** - Full command-line control with flexible options
* 📁 **Organized Downloads** - Files organized by page number with proper timestamps

---

## ⚡ Quick Start

### 1. Get Your GoPro Credentials

1. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/) and **log in**
2. Press `F12` to open Developer Tools
3. Go to **Application** tab (Chrome/Edge) or **Storage** tab (Firefox/Safari)
4. Click **Cookies** → Select `https://plus.gopro.com`
5. Copy these values:
   - `gp_access_token` → This is your `AUTH_TOKEN`
   - `gp_user_id` → This is your `USER_ID`

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/maxrodrigo/gopro-plus.git
cd gopro-plus

# Create virtual environment (REQUIRED on macOS to avoid architecture issues)
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

Create a `.envrc` file with your credentials:

```bash
# Create the file
cat > .envrc << EOF
export AUTH_TOKEN='your_token_here'
export USER_ID='your_user_id_here'
EOF

# Load the credentials
source .envrc
```

### 4. Run the Script

```bash
# Preview what will be downloaded (recommended first)
./gopro --dry-run

# Download all media
./gopro

# Or download specific pages
./gopro --start-page 1 --pages 5
```

**Where are my files?** Downloads are saved in `./download/` directory, organized by page number.

---

## 🚀 Advanced Usage

<details>
<summary><b>📋 Command Options</b></summary>

```bash
# Basic usage
./gopro                              # Download all media
./gopro --dry-run                    # Preview only, no download
./gopro --start-page 5 --pages 10    # Download pages 5-14
./gopro --per-page 10                # Smaller batches (default: 30)

# Performance options
./gopro --max-retries 10             # More retry attempts (default: 5)
./gopro --per-page 5                 # Smaller ZIP files for unstable connections

# Output options
./gopro --download-path /path/to/dir # Custom download directory

# Export media IDs
./gopro --export-ids media_ids.txt   # Export all media IDs to file
./gopro --export-ids -               # Export to stdout (for piping)
```

</details>

<details>
<summary><b>🗑️ Delete Media from GoPro Cloud</b></summary>

**⚠️ WARNING: Deletion is permanent and cannot be undone!**

The `delete_media.py` script allows you to bulk delete media from your GoPro Plus cloud storage.

### Step 1: Export Media IDs

First, get the IDs of media you want to delete:

```bash
# Export all media IDs
./gopro --pages 999 --per-page 100 --export-ids all_media_ids.txt

# Export specific page range
./gopro --start-page 1 --pages 5 --per-page 100 --export-ids first_500_ids.txt

# Export to stdout
./gopro --pages 999 --per-page 100 --export-ids -
```

### Step 2: Delete Media

```bash
# Delete from a file (one ID per line)
python3 delete_media.py --file media_ids.txt

# Delete specific IDs directly
python3 delete_media.py --ids WlVap4wRO55kZ,oKawQQ5qRJ7BP,LRW7Mkd6RKnbX

# Dry run to preview (recommended first!)
python3 delete_media.py --file media_ids.txt --dry-run
```

### Features

- **Batch deletion**: Automatically handles API limit of 100 IDs per request
- **Safety confirmation**: Prompts before deleting
- **Dry-run mode**: Preview what will be deleted without actually deleting
- **Progress tracking**: Real-time progress with Rich UI
- **Multiple input methods**: File or command-line IDs

### Example Workflow

```bash
# 1. Export all media IDs
./gopro --pages 999 --per-page 100 --export-ids all_media.txt

# 2. Review the file
wc -l all_media.txt  # Check how many items

# 3. Preview deletion (dry run)
python3 delete_media.py --file all_media.txt --dry-run

# 4. Delete (will ask for confirmation)
python3 delete_media.py --file all_media.txt
```

### Selective Deletion

```bash
# Delete only first 100 items
head -100 all_media.txt > first_100.txt
python3 delete_media.py --file first_100.txt

# Delete specific date range (after exporting and filtering)
grep "2024" all_media.txt > 2024_media.txt
python3 delete_media.py --file 2024_media.txt
```

**Note:** The script uses your existing `AUTH_TOKEN` and `USER_ID` from `.envrc`.

**📖 For complete deletion documentation, see [DELETE_MEDIA.md](DELETE_MEDIA.md)**

</details>

<details>
<summary><b>� Docker Option</b></summary>

```bash
# Pull and run with Docker
docker run --name gopro-downloader \
  -e AUTH_TOKEN="your_token_here" \
  -e USER_ID="your_user_id_here" \
  -v ~/gopro-downloads:/app/download \
  maxrodrigo/gopro:latest
```

Your files will be in `~/gopro-downloads/`

</details>


# Direct
./gopro --dry-run
```

---

## 🐳 Docker Configuration

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
| `DRY_RUN` | ❌ No | `false` | Set to `true` to preview without downloading |
| `START_PAGE` | ❌ No | `1` | Starting page number |
| `PAGES` | ❌ No | `1000000` | Number of pages to process |
| `PER_PAGE` | ❌ No | `15` | Items per page |
| `PROGRESS_MODE` | ❌ No | `noline` | Progress display: `inline`, `newline`, or `noline` |

## 🔑 Environment Variables

To set up `AUTH_TOKEN` and `USER_ID`, you need to extract them from your GoPro Plus account.

### Method 1: Browser Storage (Easiest) ⚡

1. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/) and **log in**
2. Open your browser's Developer Tools:
   - **Chrome/Edge**: Press `F12` → Go to **Application** tab → **Cookies** → `https://plus.gopro.com`
   - **Firefox**: Press `F12` → Go to **Storage** tab → **Cookies** → `https://plus.gopro.com`
   - **Safari**: `Cmd+Option+I` → Go to **Storage** tab → **Cookies** → `plus.gopro.com`
3. Find and copy these cookie values:
   - `gp_access_token` → Copy the **Value** (starts with `eyJhbGc...`)
   - `gp_user_id` → Copy the **Value**

### Method 2: Network Tab

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

#### ❌ Architecture Mismatch Error (macOS)
**Error:** `ImportError: incompatible architecture (have 'arm64', need 'x86_64')`

**Solution:** Always use the virtual environment:
```bash
# Create/activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# The ./gopro script automatically uses the venv Python
./gopro
```

#### ❌ OpenSSL Warning (macOS)
**Warning:** `urllib3 v2.0 only supports OpenSSL 1.1.1+`

**Solution:** This is harmless and already suppressed. No action needed.

#### ❌ Starship Timeout
**Warning:** `Executing command timed out`

**Solution:** Increase Starship timeout in `~/.config/starship.toml`:
```toml
[python]
command_timeout = 0  # No timeout
```

#### ❌ Authentication Failed
**Error:** `Authentication failed`

**Solution:** Your tokens expired. Re-authenticate:
1. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/)
2. Get fresh `AUTH_TOKEN` and `USER_ID` from cookies
3. Update your `.envrc` file

#### ❌ Download Issues
**Problem:** Downloads fail or are very slow

**Solution:** Use smaller batches:
```bash
# Smaller ZIP files for unstable connections
./gopro --per-page 10

# More retry attempts
./gopro --max-retries 10

# Process fewer pages at once
./gopro --start-page 1 --pages 5
```

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
