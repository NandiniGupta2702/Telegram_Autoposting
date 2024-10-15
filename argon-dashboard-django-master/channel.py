import pandas as pd
import argparse
import os
from telethon import TelegramClient
from telethon.errors import UserPrivacyRestrictedError, UserNotMutualContactError, UserNotParticipantError
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.sessions import StringSession
import asyncio

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process CSV and add members to Telegram channel.')
    parser.add_argument('--api_id', required=True, help='Telegram API ID')
    parser.add_argument('--api_hash', required=True, help='Telegram API Hash')
    parser.add_argument('--channel_username', required=True, help='Telegram channel username')
    parser.add_argument('--csv', required=True, help='Path to the CSV file')
    parser.add_argument('--phone_number', required=True, help='Phone number in international format')
    return parser.parse_args()

async def is_user_in_channel(client, channel_username, phone):
    try:
        user = await client.get_input_entity(phone)
        participants = await client(GetParticipantsRequest(
            channel=channel_username,
            filter=ChannelParticipantsSearch(''),
            offset=0,
            limit=1000,
            hash=0
        ))
        return any(participant.phone == phone for participant in participants.users)
    except Exception as e:
        print(f"Error checking if user {phone} is in the telegram: {str(e)}")
        return False

async def add_members_to_channel(api_id, api_hash, channel_username, csv_file_path, phone_number):
    session_file = f"session_{phone_number.replace('+', '')}.txt"
    session_string = ""

    if os.path.exists(session_file):
        print(f"Using existing session file: {session_file}")
        with open(session_file, "r") as file:
            session_string = file.read()

    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    await client.start(phone_number)
    print("Bot is running...")

    df = pd.read_csv(csv_file_path, header=None)
    print(f"Loaded {len(df)} entries from CSV.")

    channel = await client.get_entity(channel_username)

    for index, row in df.iterrows():
        phone = str(row[0]).strip()
        if pd.isna(phone) or not phone:
            print(f"Skipping empty or invalid phone number at row {index + 1}")
            continue

        phone = '+' + phone
        print(f"Processing phone number: {phone}")

        if await is_user_in_channel(client, channel_username, phone):
            print(f"User {phone} is already in the channel.")
            continue

        try:
            user = await client.get_input_entity(phone)
            await client(InviteToChannelRequest(channel, [user]))
            print(f"Added {phone} to the channel")
        except (UserPrivacyRestrictedError, UserNotMutualContactError, UserNotParticipantError) as e:
            print(f"Cannot add {phone}: {str(e)}")
        except Exception as e:
            print(f"Error adding {phone}: {str(e)}")

    print("All members processed.")

if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(add_members_to_channel(args.api_id, args.api_hash, args.channel_username, args.csv, args.phone_number))
