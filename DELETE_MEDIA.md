# 🗑️ GoPro Media Deletion Guide

**⚠️ WARNING: Deletion is permanent and cannot be undone!**

This guide explains how to bulk delete media from your GoPro Plus cloud storage using the `delete_media.py` script.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Examples](#examples)
- [API Details](#api-details)
- [Safety Features](#safety-features)

---

## Prerequisites

1. **Authentication**: Ensure your `.envrc` file contains valid credentials:
   ```bash
   export AUTH_TOKEN='your_token_here'
   export USER_ID='your_user_id_here'
   ```

2. **Dependencies**: The script uses the same dependencies as the main downloader (already installed if you followed the setup).

---

## Quick Start

### 1. Export Media IDs

First, get the IDs of all your media:

```bash
./gopro --pages 999 --per-page 100 --export-ids all_media_ids.txt
```

This creates a file with one media ID per line.

### 2. Preview Deletion (Dry Run)

**Always do a dry run first!**

```bash
python3 delete_media.py --file all_media_ids.txt --dry-run
```

This shows what will be deleted without actually deleting anything.

### 3. Delete Media

```bash
python3 delete_media.py --file all_media_ids.txt
```

The script will:
- Show how many items will be deleted
- Ask for confirmation
- Delete in batches of 100 (API limit)
- Show progress in real-time

---

## Detailed Usage

### Command-Line Options

```bash
python3 delete_media.py [OPTIONS]

Options:
  --ids TEXT        Comma-separated media IDs to delete
  --file PATH       File containing media IDs (one per line)
  --dry-run         Preview without deleting
  --help            Show help message
```

### Input Methods

#### Method 1: From File (Recommended)

```bash
# Create a file with IDs (one per line)
./gopro --export-ids media_ids.txt

# Delete from file
python3 delete_media.py --file media_ids.txt
```

#### Method 2: Direct IDs

```bash
python3 delete_media.py --ids WlVap4wRO55kZ,oKawQQ5qRJ7BP,LRW7Mkd6RKnbX
```

#### Method 3: Mixed (File + Additional IDs)

```bash
python3 delete_media.py --file media_ids.txt --ids AdditionalID1,AdditionalID2
```

---

## Examples

### Delete All Media

```bash
# 1. Export all IDs
./gopro --pages 999 --per-page 100 --export-ids all_media.txt

# 2. Check count
wc -l all_media.txt

# 3. Dry run
python3 delete_media.py --file all_media.txt --dry-run

# 4. Delete (with confirmation)
python3 delete_media.py --file all_media.txt
```

### Delete Specific Pages

```bash
# Export only pages 1-5 (500 items with per-page=100)
./gopro --start-page 1 --pages 5 --per-page 100 --export-ids first_500.txt

# Delete them
python3 delete_media.py --file first_500.txt
```

### Selective Deletion

```bash
# Export all IDs
./gopro --pages 999 --per-page 100 --export-ids all_media.txt

# Delete only first 100 items
head -100 all_media.txt > first_100.txt
python3 delete_media.py --file first_100.txt

# Delete items 101-200
sed -n '101,200p' all_media.txt > items_101_200.txt
python3 delete_media.py --file items_101_200.txt
```

### Delete with Filtering

If you have additional metadata, you can filter before deletion:

```bash
# Example: Delete only items from a specific date (requires custom filtering)
# This is just an example - you'd need to correlate IDs with dates from API
grep "specific_pattern" all_media.txt > filtered.txt
python3 delete_media.py --file filtered.txt
```

---

## API Details

### Endpoint

```
DELETE https://api.gopro.com/media?ids=<comma_separated_ids>
```

### Limits

- **Maximum IDs per request**: 100
- The script automatically batches requests to respect this limit

### Authentication

Uses the same cookies as the download script:
- `gp_access_token` (from `AUTH_TOKEN`)
- `gp_user_id` (from `USER_ID`)

### Response Codes

- `200` or `204`: Success
- `401`: Authentication failed (refresh your tokens)
- `400`: Invalid request (check ID format)

---

## Safety Features

### 1. Dry Run Mode

Always test with `--dry-run` first:

```bash
python3 delete_media.py --file media_ids.txt --dry-run
```

Shows:
- Total items to delete
- Number of batches
- Sample IDs from each batch

### 2. Confirmation Prompt

Before deletion, the script shows:
```
WARNING: This will permanently delete media from GoPro cloud!
Are you sure you want to delete 1025 items? [y/n]:
```

Type `n` to cancel, `y` to proceed.

### 3. Progress Tracking

Real-time progress shows:
- Current batch being processed
- Success/failure status per batch
- Final summary with counts

### 4. Error Handling

- Network errors are caught and reported
- Failed batches are logged
- Script continues with remaining batches even if one fails

---

## Troubleshooting

### Authentication Errors

**Error**: `401 Unauthorized`

**Solution**: Refresh your tokens:
1. Go to [GoPro Plus Media Library](https://plus.gopro.com/media-library/)
2. Get new `AUTH_TOKEN` and `USER_ID` from cookies
3. Update `.envrc` and reload: `source .envrc`

### Invalid IDs

**Error**: `400 Bad Request`

**Solution**: Ensure IDs are valid:
- IDs should be alphanumeric strings (e.g., `WlVap4wRO55kZ`)
- No spaces or special characters
- One ID per line in file

### Partial Deletion

**Problem**: Some batches fail

**Solution**: 
1. Check the summary output for failed batches
2. Re-export IDs and compare with what's left
3. Retry deletion for remaining items

---

## Best Practices

1. **Always dry-run first**: Use `--dry-run` to verify before deleting
2. **Backup IDs**: Keep a copy of the ID file before deletion
3. **Delete in stages**: For large deletions, do it in smaller batches
4. **Verify after deletion**: Re-export IDs to confirm deletion
5. **Download first**: If you want to keep the media, download it before deleting

---

## Example: Complete Workflow

```bash
# 1. Export all media IDs
./gopro --pages 999 --per-page 100 --export-ids all_media_ids.txt

# 2. Backup the ID file
cp all_media_ids.txt all_media_ids.backup.txt

# 3. Check count
wc -l all_media_ids.txt
# Output: 1025 all_media_ids.txt

# 4. Dry run to preview
python3 delete_media.py --file all_media_ids.txt --dry-run
# Output shows batches and sample IDs

# 5. Delete with confirmation
python3 delete_media.py --file all_media_ids.txt
# Output:
# Total media items to delete: 1025
# Batches: 11 (max 100 per batch)
# 
# WARNING: This will permanently delete media from GoPro cloud!
# Are you sure you want to delete 1025 items? [y/n]: y
# 
# ✓ Batch 1: Deleted 100 items
# ✓ Batch 2: Deleted 100 items
# ...
# ✓ Batch 11: Deleted 25 items
# 
# Summary:
#   Deleted: 1025
#   Failed:  0

# 6. Verify deletion
./gopro --pages 999 --per-page 100 --export-ids verify.txt
wc -l verify.txt
# Output: 0 verify.txt (if all deleted successfully)
```

---

## Notes

- Deletion is **permanent** - GoPro does not provide an "undo" or "trash" feature
- Deleted media cannot be recovered
- The script does not download media before deletion
- Always ensure you have backups if you want to keep the media

---

## Support

For issues or questions:
1. Check this documentation
2. Review the main [README.md](README.md)
3. Open an issue on GitHub
