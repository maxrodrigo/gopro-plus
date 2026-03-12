#!/usr/bin/env python3
import os
import sys
import warnings

# Suppress urllib3 OpenSSL warning on macOS (must be before importing requests)
warnings.filterwarnings('ignore', message='urllib3 v2.0 only supports OpenSSL 1.1.1+')

import requests
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

load_dotenv(dotenv_path='.envrc')

console = Console()

class GoProDeleter:
    def __init__(self, auth_token, user_id):
        self.base_url = "https://api.gopro.com"
        self.auth_token = auth_token
        self.user_id = user_id
    
    def default_headers(self):
        return {
            "Accept": "application/vnd.gopro.jk.media+json; version=2.0.0",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
    
    def default_cookies(self):
        return {
            "gp_access_token": self.auth_token,
            "gp_user_id": self.user_id,
        }
    
    def delete_media(self, media_ids, dry_run=False):
        """Delete media by IDs. Max 100 IDs per request."""
        if not media_ids:
            console.print("[yellow]No media IDs provided[/yellow]")
            return
        
        # Split into batches of 100
        batch_size = 100
        batches = [media_ids[i:i + batch_size] for i in range(0, len(media_ids), batch_size)]
        
        console.print(f"[cyan]Total media items to delete: {len(media_ids)}[/cyan]")
        console.print(f"[cyan]Batches: {len(batches)} (max {batch_size} per batch)[/cyan]")
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - No deletions will be performed[/yellow]\n")
            for i, batch in enumerate(batches, 1):
                console.print(f"[blue]Batch {i}:[/blue] {len(batch)} items")
                console.print(f"  IDs: {', '.join(batch[:5])}{'...' if len(batch) > 5 else ''}")
            return
        
        # Confirm deletion
        console.print("\n[bold red]WARNING: This will permanently delete media from GoPro cloud![/bold red]")
        if not Confirm.ask(f"Are you sure you want to delete {len(media_ids)} items?"):
            console.print("[yellow]Deletion cancelled[/yellow]")
            return
        
        deleted_count = 0
        failed_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Deleting media...", total=len(batches))
            
            for i, batch in enumerate(batches, 1):
                ids_param = ",".join(batch)
                url = f"{self.base_url}/media"
                params = {"ids": ids_param}
                
                progress.update(task, description=f"Deleting batch {i}/{len(batches)} ({len(batch)} items)")
                
                try:
                    resp = requests.delete(
                        url,
                        params=params,
                        headers=self.default_headers(),
                        cookies=self.default_cookies(),
                        timeout=30
                    )
                    
                    if resp.status_code in [200, 204]:
                        deleted_count += len(batch)
                        console.print(f"[green]✓ Batch {i}: Deleted {len(batch)} items[/green]")
                    else:
                        failed_count += len(batch)
                        console.print(f"[red]✗ Batch {i} failed: {resp.status_code} - {resp.text}[/red]")
                
                except Exception as e:
                    failed_count += len(batch)
                    console.print(f"[red]✗ Batch {i} error: {e}[/red]")
                
                progress.advance(task)
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Deleted: [green]{deleted_count}[/green]")
        console.print(f"  Failed:  [red]{failed_count}[/red]")

def main():
    parser = argparse.ArgumentParser(
        description="Delete GoPro media from cloud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Delete specific IDs
  %(prog)s --ids WlVap4wRO55kZ,oKawQQ5qRJ7BP,LRW7Mkd6RKnbX
  
  # Delete IDs from a file (one ID per line)
  %(prog)s --file media_ids.txt
  
  # Dry run to preview
  %(prog)s --ids WlVap4wRO55kZ,oKawQQ5qRJ7BP --dry-run
        """
    )
    parser.add_argument("--ids", help="Comma-separated media IDs to delete")
    parser.add_argument("--file", help="File containing media IDs (one per line)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    
    args = parser.parse_args()
    
    if not args.ids and not args.file:
        parser.error("Must provide either --ids or --file")
    
    if "AUTH_TOKEN" not in os.environ:
        console.print("[red]ERROR: AUTH_TOKEN not set in environment[/red]")
        return 1
    
    if "USER_ID" not in os.environ:
        console.print("[red]ERROR: USER_ID not set in environment[/red]")
        return 1
    
    auth_token = os.environ["AUTH_TOKEN"]
    user_id = os.environ["USER_ID"]
    
    # Collect media IDs
    media_ids = []
    
    if args.ids:
        media_ids.extend([id.strip() for id in args.ids.split(",") if id.strip()])
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_ids = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                media_ids.extend(file_ids)
        except FileNotFoundError:
            console.print(f"[red]ERROR: File not found: {args.file}[/red]")
            return 1
    
    # Remove duplicates while preserving order
    media_ids = list(dict.fromkeys(media_ids))
    
    if not media_ids:
        console.print("[yellow]No media IDs found[/yellow]")
        return 1
    
    deleter = GoProDeleter(auth_token, user_id)
    deleter.delete_media(media_ids, dry_run=args.dry_run)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
