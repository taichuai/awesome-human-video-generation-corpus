##  安装 you-get
# pip install you-get

import os
import time
import random
from concurrent.futures import ThreadPoolExecutor
import subprocess
import argparse

# Configuration parameters
class Config:
    DOWNLOAD_DIR = "bilibili_downloads"  # Download directory
    MAX_WORKERS = 2  # Maximum concurrent downloads
    MIN_DELAY = 20  # Minimum delay in seconds
    MAX_DELAY = 40  # Maximum delay in seconds
    RETRY_TIMES = 2  # Number of retry attempts

# Create download directory
os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

def download_video(url):
    """Download a single video"""
    retry_count = 0
    while retry_count < Config.RETRY_TIMES:
        try:
            # Random delay
            delay = random.uniform(Config.MIN_DELAY, Config.MAX_DELAY)
            print(f"Waiting {delay:.1f} seconds before downloading: {url}")
            time.sleep(delay)
            
            # Download using you-get
            print(f"Starting download: {url}")
            cmd = [
                'you-get',
                '-o', Config.DOWNLOAD_DIR,
                '--no-proxy',
                url
            ]
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if process.returncode == 0:
                print(f"Successfully downloaded: {url}")
                return True
            else:
                print(f"Download failed: {url}")
                print(f"Error message: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"Download timeout: {url}")
        except Exception as e:
            print(f"Download error: {url}")
            print(f"Error details: {str(e)}")
            
        retry_count += 1
        if retry_count < Config.RETRY_TIMES:
            print(f"Retrying in 10 seconds... Attempt {retry_count + 1}")
            time.sleep(10)
    
    return False

def read_urls(filename):
    """Read URLs from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and line.startswith('http')]
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return []

def main(url_file):
    # Read URL list
    urls = read_urls(url_file)
    if not urls:
        print("No valid URLs found. Please check the file content.")
        return
    
    print(f"Found {len(urls)} video links")
    print(f"Videos will be downloaded to: {os.path.abspath(Config.DOWNLOAD_DIR)}")
    print(f"Starting download with max concurrent downloads: {Config.MAX_WORKERS}")
    
    # Track successful and failed URLs
    failed_urls = []
    success_count = 0
    
    # Download using thread pool
    with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
        futures = [executor.submit(download_video, url) for url in urls]
        for url, future in zip(urls, futures):
            try:
                if future.result():
                    success_count += 1
                else:
                    failed_urls.append(url)
            except Exception as e:
                print(f"Error processing download result: {str(e)}")
                failed_urls.append(url)
    
    # Save failed URLs to file
    if failed_urls:
        failed_file = "failed_downloads.txt"
        try:
            with open(failed_file, 'w', encoding='utf-8') as f:
                for url in failed_urls:
                    f.write(url + '\n')
            print(f"Failed URLs have been saved to: {failed_file}")
        except Exception as e:
            print(f"Error saving failed URLs: {str(e)}")
    
    # Print statistics
    print("\nDownload Statistics:")
    print(f"Total: {len(urls)} videos")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(failed_urls)}")

if __name__ == "__main__":
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description='Bilibili Video Batch Downloader')
    parser.add_argument('--url_file', , default="bili_url.txt", help='Path to the file containing video URLs')
    args = parser.parse_args()
    
    print("Bilibili Video Batch Downloader Starting...")
    
    # Check if you-get is installed
    try:
        subprocess.run(['you-get', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: you-get not found. Please install it first:")
        print("pip install you-get")
        exit(1)
    
    start_time = time.time()
    main(args.url_file)
    end_time = time.time()
    
    print(f"\nTotal time elapsed: {(end_time-start_time)/60:.2f} minutes")
