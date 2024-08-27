import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Variables loaded from the environment
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# YouTube API setup
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def search_channel_by_handle(handle):
    handle = handle.lstrip('@')
    print(f"Searching for channel by handle: {handle}")
    
    try:
        request = youtube.search().list(
            part='snippet',
            q=handle,
            type='channel',
            maxResults=1
        )
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            channel_id = response['items'][0]['snippet']['channelId']
            channel_title = response['items'][0]['snippet']['title']
            print(f"Found channel: {channel_title} with ID: {channel_id}")
            return channel_id
        else:
            print(f"No channel found for handle: {handle}")
    except Exception as e:
        print(f"Error during search by handle: {str(e)}")

    return None

def get_channel_by_custom_url(url):
    handle = url.split('@')[1].strip('/')
    print(f"Attempting to retrieve channel ID by custom URL for handle: {handle}")
    
    try:
        request = youtube.channels().list(
            part='id,snippet',
            forUsername=handle
        )
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            channel_id = response['items'][0]['id']
            channel_title = response['items'][0]['snippet']['title']
            print(f"Found channel: {channel_title} with ID: {channel_id}")
            return channel_id
        else:
            print(f"No channel found for custom URL handle: {handle}")
    except Exception as e:
        print(f"Error during retrieval by custom URL: {str(e)}")

    return None

def get_channel_by_id(channel_id):
    print(f"Retrieving channel info by known channel ID: {channel_id}")
    
    try:
        request = youtube.channels().list(
            part='id,snippet',
            id=channel_id
        )
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            channel_title = response['items'][0]['snippet']['title']
            print(f"Found channel: {channel_title} with ID: {channel_id}")
            return channel_id
        else:
            print(f"No channel found for ID: {channel_id}")
    except Exception as e:
        print(f"Error during retrieval by ID: {str(e)}")

    return None

def main():
    # Example handles, URLs, and IDs
    handles = ["@CocoRules_", "@perfectmilk7807"]
    custom_urls = ["https://www.youtube.com/@CocoRules_", "https://www.youtube.com/@perfectmilk7807"]
    known_channel_ids = ["UCxxxxxxxxxxxxxxxxx", "UCyyyyyyyyyyyyyyyyy"]

    for handle in handles:
        print("\n--- Searching by Handle ---")
        search_channel_by_handle(handle)
    
    for url in custom_urls:
        print("\n--- Retrieving by Custom URL ---")
        get_channel_by_custom_url(url)

    for channel_id in known_channel_ids:
        print("\n--- Retrieving by Channel ID ---")
        get_channel_by_id(channel_id)

if __name__ == "__main__":
    main()
