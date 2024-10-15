# import pandas as pd
# from telethon.sync import TelegramClient
# from telethon.errors import SessionPasswordNeededError

# # Function to fetch participants
# def fetch_group_users(api_id, api_hash, phone_number, group_username, session_name="session"):
#     # Create a new TelegramClient session
#     client = TelegramClient(session_name, api_id, api_hash)
    
#     try:
#         # Start the client session
#         client.start(phone_number)

#         # Get participants from the group or channel
#         print(f"Fetching participants from {group_username}...")
#         participants = client.get_participants(group_username)

#         # Initialize lists to store user details
#         firstname = []
#         lastname = []
#         username = []

#         if participants:
#             for x in participants:
#                 firstname.append(x.first_name or '')
#                 lastname.append(x.last_name or '')
#                 username.append(x.username or '')
            
#             # Convert list to DataFrame
#             data = {
#                 'first_name': firstname,
#                 'last_name': lastname,
#                 'user_name': username
#             }
#             userdetails = pd.DataFrame(data)
#             print("Participants fetched successfully.")
#             return userdetails
#         else:
#             print(f"No participants found for {group_username}")
#             return None

#     except SessionPasswordNeededError:
#         print("Two-step verification is enabled. Please provide your password.")
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#     finally:
#         # Disconnect the client after processing
#         client.disconnect()

# # Function to save DataFrame to CSV
# def save_to_csv(dataframe, filename="group_users.csv"):
#     if dataframe is not None:
#         dataframe.to_csv(filename, index=False)
#         print(f"Data saved to {filename}")
#     else:
#         print("No data to save.")

# # Example usage
# if __name__ == "__main__":
#     # Telegram API credentials
#     api_id = 25067216  # Your API ID
#     api_hash = "85233d61d7cf88f831519fe92a418408"  # Your API Hash
#     phone_number = "+917905468330"  # Your Telegram phone number
#     group_username = "@amazonindiaassociates"  # Group or Channel username

#     # Fetch participants and store in a DataFrame
#     user_details_df = fetch_group_users(api_id, api_hash, phone_number, group_username)

#     # Save to CSV if data is fetched
#     save_to_csv(user_details_df, "group_users.csv")

from telethon.sync import TelegramClient
import pandas as pd

# Your API credentials
api_id = 25067216
api_hash = '85233d61d7cf88f831519fe92a418408'
phone = '+917905468330'

# Initialize Telegram client
client = TelegramClient(phone, api_id, api_hash)

# Connect to the client
client.start()

# Replace with your group username
group_username = '@Deals_Offerzone_Loots'

# Fetch participants from the group
participants = client.get_participants(group_username)

# Lists to hold user data
firstname = []
lastname = []
username = []

# Extract first name, last name, and username
if len(participants):
    for user in participants:
        firstname.append(user.first_name)
        lastname.append(user.last_name)
        username.append(user.username)

# Create a dictionary for DataFrame conversion
data = {
    'first_name': firstname,
    'last_name': lastname,
    'username': username
}

# Convert dictionary to DataFrame
userdetails = pd.DataFrame(data)

# Save DataFrame to CSV
userdetails.to_csv('user_details.csv', index=False)

print("User details saved to 'user_details.csv'")

# Disconnect the client after fetching data
client.disconnect()
