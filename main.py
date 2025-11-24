import os
import sys
import json
import argparse
import signal
import readchar
import requests
import time
from requests.exceptions import ChunkedEncodingError, ConnectionError, Timeout


sys.stdout = open(1, "w", encoding="utf-8", closefd=False)

def handler(signum, frame):
    print("\ninterrupting the process. do you really want to exit? (y/n) ")

    res = readchar.readchar()
    if res == 'y':
        print("stopping the process!")
        exit(1)
    else:
        print("continue executing...")

signal.signal(signal.SIGINT, handler)


class GoProPlus:
    def __init__(self, auth_token, user_id):
        self.base = "api.gopro.com"
        self.host = "https://{}".format(self.base)
        self.auth_token = auth_token
        self.user_id = user_id

    def default_headers(self):
        return {
            "Accept": "application/vnd.gopro.jk.media+json; version=2.0.0",
            "Accept-Language": "en-US,en;q=0.9,bg;q=0.8,es;q=0.7",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

    def default_cookies(self):
        return {
            "gp_access_token": self.auth_token,
            "gp_user_id": self.user_id,
        }

    def validate(self):
        url = f"{self.host}/media/user"
        resp = requests.get(
                url,
                headers=self.default_headers(),
                cookies=self.default_cookies(),
        )

        if resp.status_code != 200:
            print("Failed to validate auth token. Issue a new one.")
            print(f"Status code: {resp.status_code}")
            return False

        return True

    def parse_error(self, resp):
        try:
            err = resp.json()
        except:
            err = resp.text
        return err

    def get_ids_from_media(self, media):
        return [x["id"] for x in media]

    def get_filenames_from_media(self, media):
        return [x["filename"] for x in media]

    def get_media(self, start_page=1, pages=sys.maxsize, per_page=30):
        url= "{}/media/search".format(self.host)

        output_media = {}
        total_pages = 0
        current_page = start_page
        while True:
            params = {
                # for all fields check some requests on GoProPlus website requests
                "per_page": per_page,
                "page": current_page,
                "fields": "id,created_at,content_title,filename,file_extension",
            }

            resp = requests.get(
                url,
                params=params,
                headers=self.default_headers(),
                cookies=self.default_cookies()
            )
            if resp.status_code != 200:
                err = self.parse_error(resp)
                print("failed to get media for page {}: {}. try renewing the auth token".format(current_page, err))
                return []

            content = resp.json()
            output_media[current_page] = content["_embedded"]["media"]
            print("page parsed ({}/{})".format(current_page, total_pages))

            if total_pages == 0:
                total_pages = content["_pages"]["total_pages"]

            if current_page >= total_pages or current_page >= (start_page + pages) - 1:
                break

            current_page += 1

        return output_media


    def download_media_ids(self, ids, filepath, progress_mode="inline", max_retries=5):
        url = "{}/media/x/zip/source".format(self.host)
        params = {
            "ids": ",".join(ids),
            "access_token": self.auth_token,
        }

        # Check if file already exists and is complete
        if os.path.exists(filepath):
            try:
                # Get expected file size from server
                head_resp = requests.head(
                    url,
                    params=params,
                    headers=self.default_headers(),
                    cookies=self.default_cookies(),
                    timeout=10
                )
                
                if head_resp.status_code == 200 and 'Content-Length' in head_resp.headers:
                    expected_size = int(head_resp.headers['Content-Length'])
                    actual_size = os.path.getsize(filepath)
                    
                    if actual_size == expected_size:
                        print(f"file already exists and is complete: {filepath} ({actual_size} bytes)")
                        return True
                    else:
                        print(f"file exists but incomplete: {actual_size}/{expected_size} bytes, re-downloading...")
                        os.remove(filepath)
                else:
                    # HEAD request didn't return Content-Length, validate ZIP can be opened
                    import zipfile
                    try:
                        with zipfile.ZipFile(filepath, 'r') as zip_ref:
                            # Just check if ZIP can be opened and has files
                            if len(zip_ref.namelist()) > 0:
                                print(f"file already exists and is valid: {filepath}")
                                return True
                        print(f"existing file is empty, re-downloading...")
                        os.remove(filepath)
                    except (zipfile.BadZipFile, Exception) as zip_err:
                        print(f"existing file is corrupted: {zip_err}, re-downloading...")
                        os.remove(filepath)
            except Exception as e:
                print(f"could not validate existing file: {e}, re-downloading...")
                try:
                    os.remove(filepath)
                except:
                    pass

        temp_filepath = filepath + ".tmp"
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Remove any existing temp file - ZIP files cannot be resumed
                # because they are dynamically generated and would be corrupted
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                
                print('downloading to {}'.format(filepath))
                
                resp = requests.get(
                    url,
                    params=params,
                    headers=self.default_headers(),
                    cookies=self.default_cookies(),
                    stream=True,
                    timeout=30)

                if resp.status_code != 200:
                    print("request failed with status code: {} and error: {}".format(resp.status_code, self.parse_error(resp)))
                    return False
                
                downloaded_size = 0
                with open(temp_filepath, 'wb') as file:
                    # Iterate over the response in chunks 8K chunks
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive chunks
                            # Write the chunk to the file
                            file.write(chunk)

                            # Update the downloaded size
                            downloaded_size += len(chunk)
                            progress = ((downloaded_size / 1024) / 1024)

                            if progress_mode == "inline":
                                # Print the progress
                                print(f"\rdownloaded: {progress:.2f}MB ({downloaded_size}) bytes", end='')

                            if progress_mode == "newline":
                                print(f"downloaded: {progress:.2f}MB ({downloaded_size}) bytes")

                # Download completed successfully, rename temp file to final name
                if os.path.exists(filepath):
                    os.remove(filepath)
                os.rename(temp_filepath, filepath)
                print("\ndownload completed!")
                return True
                
            except (ChunkedEncodingError, ConnectionError, Timeout) as e:
                retry_count += 1
                if retry_count > max_retries:
                    print(f"\ndownload failed after {max_retries} retries: {e}")
                    # Clean up temp file on final failure
                    if os.path.exists(temp_filepath):
                        os.remove(temp_filepath)
                    return False
                
                wait_time = min(2 ** retry_count, 60)  # exponential backoff, max 60s
                print(f"\nconnection error: {e}")
                print(f"retrying in {wait_time}s (attempt {retry_count}/{max_retries})...")
                time.sleep(wait_time)
            
            except Exception as e:
                print(f"\nunexpected error during download: {e}")
                # Clean up temp file on error
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                return False
        
        return False


def main():
    actions = ["list", "download"]
    progress_modes = ["inline", "newline", "noline"]

    parser = argparse.ArgumentParser(prog="gopro")
    parser.add_argument("--action", help="action to execute. supported actions: {}".format(",".join(actions)), default="download")
    parser.add_argument("--pages", nargs="?", help="number of pages to iterate over", type=int, default=sys.maxsize)
    parser.add_argument("--per-page", nargs="?", help="number of items per page", type=int, default=30)
    parser.add_argument("--start-page", nargs="?", help="starting page", type=int, default=1)
    parser.add_argument("--download-path", help="path to store the download zip", default="./download")
    parser.add_argument("--progress-mode", help="showing download progress. supported modes: {}".format(",".join(progress_modes)), default=progress_modes[0])
    parser.add_argument("--max-retries", nargs="?", help="maximum number of retries for failed downloads", type=int, default=5)

    args = parser.parse_args()

    if "AUTH_TOKEN" not in os.environ:
        print("invalid AUTH_TOKEN env variable set")
        return

    if "USER_ID" not in os.environ:
        print("invalid USER_ID env variable set")
        return

    auth_token = os.environ["AUTH_TOKEN"]
    user_id = os.environ["USER_ID"]
    gpp = GoProPlus(auth_token, user_id)
    if not gpp.validate():
        return -1

    media_pages = gpp.get_media(start_page=args.start_page, pages=args.pages, per_page=args.per_page)
    if not media_pages:
        print('failed to get media')
        return -1

    # Ensure download directory exists
    if args.action == "download":
        os.makedirs(args.download_path, exist_ok=True)

    for page, media in media_pages.items():
        filenames = gpp.get_filenames_from_media(media)
        print("listing page({}) media({})".format(page, filenames))

        if args.action == "download":
            filepath = "{}/{}_page.zip".format(args.download_path, page)
            ids = gpp.get_ids_from_media(media)
            gpp.download_media_ids(ids, filepath, progress_mode=args.progress_mode, max_retries=args.max_retries)


if __name__ == "__main__":
    main()
