import os
import discord
from discord.ext import tasks, commands
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Variables loaded from the environment
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
VIDEOS_CHANNEL_ID = int(os.getenv('VIDEOS_CHANNEL_ID'))
SHORTS_CHANNEL_ID = int(os.getenv('SHORTS_CHANNEL_ID'))
POSTED_VIDEOS_FILE = 'posted_videos.txt'
CHANNEL_CONFIG_FILE = 'channel_config.txt'

# YouTube API setup
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Set up Discord intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Discord Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

def read_posted_videos():
    if os.path.exists(POSTED_VIDEOS_FILE):
        with open(POSTED_VIDEOS_FILE, 'r') as file:
            return file.read().splitlines()
    return []

def write_posted_video(video_id):
    with open(POSTED_VIDEOS_FILE, 'a') as file:
        file.write(video_id + '\n')

def read_channel_configs():
    # Read channel IDs directly from the config file
    channels = []
    if os.path.exists(CHANNEL_CONFIG_FILE):
        with open(CHANNEL_CONFIG_FILE, 'r') as file:
            channels = [line.strip() for line in file if line.strip()]
    return channels

def is_youtube_short(video_url):
    # Check if the URL contains "/shorts/"
    return '/shorts/' in video_url

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    check_new_video.start()  # Start the loop to check for new videos

@tasks.loop(minutes=30)
async def check_new_video():
    try:
        print("Checking for new videos...")
        channel_ids = read_channel_configs()

        for channel_id in channel_ids:
            print(f"Checking channel: {channel_id}")
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                order='date',
                type='video',
                maxResults=1
            )
            response = request.execute()

            if 'items' in response and len(response['items']) > 0:
                latest_video = response['items'][0]
                video_id = latest_video['id']['videoId']
                posted_videos = read_posted_videos()

                if video_id and video_id not in posted_videos:
                    write_posted_video(video_id)
                    video_title = latest_video['snippet']['title']
                    video_url = f'https://www.youtube.com/watch?v={video_id}'

                    # Determine the appropriate channel based on video type
                    if is_youtube_short(video_url):
                        channel = bot.get_channel(SHORTS_CHANNEL_ID)
                    else:
                        channel = bot.get_channel(VIDEOS_CHANNEL_ID)

                    message = f'🎥 **New Video Uploaded:**\n{video_title}\n{video_url}'

                    if channel:
                        if not channel.permissions_for(channel.guild.me).send_messages:
                            print(f"Do not have permission to send messages in {channel.name}")
                            return
                        await channel.send(message)
                        print(f"Posted new video: {video_title} in {channel.name}")
                    else:
                        print("Channel not found.")
                else:
                    print("No new video or same video found.")
            else:
                print(f"No new videos found in the latest API response for channel {channel_id}.")

    except Exception as e:
        print(f"Error during YouTube video check: {e}")

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
