
import os
import django
import asyncio
import re
import aiohttp
import httpx
from urllib.parse import urlparse
from telethon import TelegramClient
from telethon.sessions import StringSession
from asgiref.sync import sync_to_async
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  
django.setup()
# from apps.authentication.models import MinId  
from apps.authentication.models import ChannelMinId  

def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Bot Script')
    parser.add_argument('--token', required=True, help='Bot token')
    parser.add_argument('--api_id', required=True, help='API ID')
    parser.add_argument('--api_hash', required=True, help='API Hash')
    parser.add_argument('--group_username', required=True, help='Group username')
    parser.add_argument('--channel_username', required=True, help='Channel username')
    parser.add_argument('--api_key', required=True, help='API key')
    parser.add_argument('--phone_number', required=True, help='Phone number in international format')
    args = parser.parse_args()

    print(f"Phone number: {args.phone_number}")
    return args

async def get_min_id(source_channel, destination_channel, phone_number):
    return await sync_to_async(lambda: ChannelMinId.objects.filter(
        source_channel=source_channel,
        destination_channel=destination_channel,
        phone_number=phone_number
    ).first())()

async def update_min_id(source_channel, destination_channel, phone_number, min_id):
    await sync_to_async(lambda: ChannelMinId.objects.update_or_create(
        source_channel=source_channel,
        destination_channel=destination_channel,
        phone_number=phone_number,
        defaults={'min_id': min_id}
    ))()

async def main():
    args = parse_args()
    session_file = f"session_{args.phone_number.replace('+', '')}.txt"

    if os.path.exists(session_file):
        print(f"Session file '{session_file}' already exists. Using existing session.")
        with open(session_file, "r") as file:
            session_string = file.read()
    else:
        print("Session file does not exist. Please check your credentials.")
        return 

    client = TelegramClient(StringSession(session_string), args.api_id, args.api_hash)
    await client.start(args.phone_number)

    print("Bot is running...")

    # Fetch min_id based on source and destination channels
    min_id_record = await get_min_id(args.group_username, args.channel_username, args.phone_number)
    min_id = min_id_record.min_id if min_id_record else 0

    messages = await client.get_messages(args.group_username, limit=1)

    if not messages:
        print("No messages found in the source channel.")
        return

    latest_message = messages[0]
    latest_message_id = latest_message.id
    print("Latest Message ID:", latest_message_id)

    if min_id == 0:
        print("First run: Posting the latest message to the destination channel...")
        await process_and_post_message(client, latest_message, args)

        min_id = latest_message_id
        print("Updated min_id to:", min_id)
    elif min_id == latest_message_id:
        print("No message to process")
    else:
        new_messages = await client.get_messages(args.group_username, min_id=min_id, max_id=latest_message_id + 1)

        for message in new_messages[::-1]:
            await process_and_post_message(client, message, args)

        min_id = latest_message_id
        print(f"Updated min_id to: {min_id}")

    # Update min_id based on source and destination channels
    await update_min_id(args.group_username, args.channel_username, args.phone_number, min_id)

async def process_and_post_message(client, message, args):
    message_text = message.text.strip()  
    message_id = message.id
    print("Processing Message ID:", message_id)

    existing_messages = await client.get_messages(args.channel_username)
    existing_message_ids = {msg.id for msg in existing_messages if msg.text}

    if message_id in existing_message_ids:  
        print(message_id, "Message already exists in the destination channel.")
        return

    url_map = await extract_urls(message_text, args.api_key)
    for original_url, deep_link in url_map.items():
        normalized_original_url = normalize_url(original_url)
        message_text = re.sub(re.escape(normalized_original_url), deep_link, message_text)
    
    if not message_text:  # Check if message_text is empty after processing
        print(f"Message ID {message_id} is empty after processing, skipping.")
        return 
    
    try:
        await client.send_message(args.channel_username, message_text)
        print("Message posted to the destination channel.")
    except Exception as e:
        print(f"Error sending message: {e}")

def normalize_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc + parsed_url.path

async def fetch_redirected_url(url: str) -> str:
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, allow_redirects=True) as response:
                    final_url = str(response.url)
                    return final_url
        except Exception as e:
            if attempt == 2:
                return url

async def convert_link_via_postman(redirected_url: str, api_key: str) -> str:
    url = api_key
    headers = {"Content-Type": "application/json"}
    payload = {"url": redirected_url}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            deep_link = response_data.get("deep_link", redirected_url)
            return deep_link
    except Exception as e:
        print(f"Error converting link via Postman: {e}")
    return redirected_url

async def extract_urls(message: str, api_key: str) -> dict[str, str]:
    urls = re.findall(r'\b(?:https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\S*)\b', message)

    urls_with_scheme = []
    for url in urls:
        if re.match(r'^[a-zA-Z][a-zA-Z\d+\-.]*:', url):
            urls_with_scheme.append(url)
        elif url.startswith('www'):
            urls_with_scheme.append(f'http://{url}')
        elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', url):
            urls_with_scheme.append(f'https://{url}')
        else:
            urls_with_scheme.append(url)

    urls_with_scheme = [url.split('#')[0] for url in urls_with_scheme]

    redirected_urls = await asyncio.gather(*(fetch_redirected_url(url) for url in urls_with_scheme))
    deep_links = await asyncio.gather(*(convert_link_via_postman(url, api_key) for url in redirected_urls))

    return dict(zip(urls_with_scheme, deep_links))

if __name__ == '__main__':
    asyncio.run(main())
