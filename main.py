import os
import sys
import json
import argparse
import signal
import readchar
import requests
import time
from requests.exceptions import ChunkedEncodingError, ConnectionError, Timeout
from rich.console import Console
from rich.progress import Progress, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, BarColumn, TextColumn
from rich.table import Table
from rich import print as rprint


sys.stdout = open(1, "w", encoding="utf-8", closefd=False)

console = Console()

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
    
    def get_media_info(self, media):
        """Extract filename and file size from media items"""
        return [(x["filename"], x.get("file_size") or 0) for x in media]

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
                "fields": "id,created_at,content_title,filename,file_extension,file_size",
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
                        console.print(f"✓ [green]File already exists and is complete:[/green] {filepath} ({actual_size} bytes)")
                        return True
                    else:
                        console.print(f"[yellow]File incomplete:[/yellow] {actual_size}/{expected_size} bytes, re-downloading...")
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
                
                resp = requests.get(
                    url,
                    params=params,
                    headers=self.default_headers(),
                    cookies=self.default_cookies(),
                    stream=True,
                    timeout=30)

                if resp.status_code != 200:
                    console.print(f"[red]✗ Request failed:[/red] {resp.status_code} - {self.parse_error(resp)}")
                    return False
                
                # Get total file size if available
                total_size = int(resp.headers.get('content-length', 0))
                
                # Use Rich progress bar
                with Progress(
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=console
                ) as progress:
                    task = progress.add_task(f"Downloading {os.path.basename(filepath)}", total=total_size)
                    
                    with open(temp_filepath, 'wb') as file:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                                progress.update(task, advance=len(chunk))

                # Download completed successfully, rename temp file to final name
                if os.path.exists(filepath):
                    os.remove(filepath)
                os.rename(temp_filepath, filepath)
                console.print(f"[green]✓ Download completed:[/green] {filepath}")
                return True
                
            except (ChunkedEncodingError, ConnectionError, Timeout) as e:
                retry_count += 1
                if retry_count > max_retries:
                    console.print(f"[red]✗ Download failed after {max_retries} retries:[/red] {e}")
                    # Clean up temp file on final failure
                    if os.path.exists(temp_filepath):
                        os.remove(temp_filepath)
                    return False
                
                wait_time = min(2 ** retry_count, 60)  # exponential backoff, max 60s
                console.print(f"[yellow]⚠ Connection error:[/yellow] {e}")
                console.print(f"[yellow]Retrying in {wait_time}s (attempt {retry_count}/{max_retries})...[/yellow]")
                time.sleep(wait_time)
            
            except Exception as e:
                console.print(f"[red]✗ Unexpected error:[/red] {e}")
                # Clean up temp file on error
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                return False
        
        return False


def main():
    progress_modes = ["inline", "newline", "noline"]

    parser = argparse.ArgumentParser(prog="gopro")
    parser.add_argument("--dry-run", action="store_true", help="preview what would be downloaded without actually downloading")
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
        console.print('[red]✗ Failed to get media[/red]')
        return -1

    # Ensure download directory exists
    if not args.dry_run:
        os.makedirs(args.download_path, exist_ok=True)

    if args.dry_run:
        # Create a compact summary table
        total_items = sum(len(media) for media in media_pages.values())
        
        def format_size(bytes_size):
            """Convert bytes to human readable format"""
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} TB"
        
        table = Table(title=f"[bold cyan]Dry Run - {total_items} items across {len(media_pages)} pages[/bold cyan]", show_header=True, header_style="bold magenta")
        table.add_column("Page", style="blue", justify="center", width=6)
        table.add_column("ZIP File", style="yellow", width=15)
        table.add_column("Items", style="green", justify="right", width=6)
        table.add_column("Total Size", style="green", justify="right", width=12)
        table.add_column("Files", style="cyan", no_wrap=False)
        
        grand_total_size = 0
        
        for page, media in media_pages.items():
            media_info = gpp.get_media_info(media)
            zip_filename = f"{page}_page.zip"
            
            # Calculate total size for this page
            total_size = sum(size for _, size in media_info)
            grand_total_size += total_size
            
            # Create compact file list without individual sizes
            filenames = [name for name, _ in media_info]
            files_display = ", ".join(filenames)
            
            table.add_row(
                str(page),
                zip_filename,
                str(len(media)),
                format_size(total_size),
                files_display
            )
        
        # Add total row
        table.add_section()
        table.add_row(
            "[bold]TOTAL[/bold]",
            "",
            f"[bold]{total_items}[/bold]",
            f"[bold]{format_size(grand_total_size)}[/bold]",
            "",
            style="bold yellow"
        )
        
        console.print(table)
    else:
        for page, media in media_pages.items():
            console.print(f"[bold blue]Page {page}[/bold blue] - Downloading {len(media)} items")
            filepath = "{}/{}_page.zip".format(args.download_path, page)
            ids = gpp.get_ids_from_media(media)
            gpp.download_media_ids(ids, filepath, progress_mode=args.progress_mode, max_retries=args.max_retries)


if __name__ == "__main__":
    main()
