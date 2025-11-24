# CHANGELOG

## 1.6.0
* Add automatic retry logic with exponential backoff for download failures
* Add HTTP Range header support to resume partial downloads from interruption point
* Add --max-retries CLI argument to configure maximum retry attempts (default: 5)
* Reset retry counter on successful progress to allow fresh retries per failure
* Add 30s timeout per request to prevent hanging connections
* Handle ChunkedEncodingError, ConnectionError, and Timeout exceptions gracefully
* Save partial downloads as .tmp files for manual recovery if all retries fail

## 1.5.3
* Fix missing download directory on the docker container
* Add entrypoint.sh script as a startup script for Docker usage
* Update README.md with the new usage that support host directory download

## 1.4.3
* Fix authentication by adding mandatory `USER_ID` and forcing requests using cookies instead of headers
* Adjust local env using USER_ID
* Makefile help section
* Dockerfile deprecation warning fixed around env variable setup

## 1.3.3
* Link Dockerfile ENV variables to execution script

## 1.3.2
* Support --start-page cli argument to support skipping already downloaded
pages of media assets

## 1.2.2
* Support --progress-mode cli argument to specify logging download progress
(in docker logs inline logging is hard to read)

## 1.2.1
* Support page scope download (minimize big bulk download interruptions and
file corruptions)
* Support arguments for number of pages and per page number of items

## 1.1.1
* Support CLI arguments
* Support separate action for listing media files
* Support separate action for downloading media files (bulk download)

## 1.0.1
* Support better progress logging

## 1.0.0
* Basic working prototype
* Support bulk download for all media library files at once
