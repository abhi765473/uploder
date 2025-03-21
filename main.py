import os
import re
import sys
import json
import cloudscraper
import time
import asyncio
from aiohttp import web
import base64
import json
import cloudscraper
import requests
import subprocess

import random

from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from content_fetcher import set_token, generate_content_file

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
photologo = 'https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png'
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png'

async def show_random_emojis(message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '🌟', '🔥', '✨']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message
    

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)
cookies_file_path = "cookies.txt"

allowed_channels = set()  # Store allowed channel IDs here
admins = [5850397219]
PORT = 8080  # Define a port number
# Replace with your admin's Telegram user ID

# Path to the file where authorized users will be saved
AUTHORIZED_USERS_FILE = "authorized_users.json"

# Load authorized users from a file (if it exists)
if os.path.exists(AUTHORIZED_USERS_FILE):
    with open(AUTHORIZED_USERS_FILE, "r") as file:
        authorized_users = json.load(file)
else:
    authorized_users = {}

def save_authorized_users():
    """Save authorized users to a file"""
    with open(AUTHORIZED_USERS_FILE, "w") as file:
        json.dump(authorized_users, file)


# Define aiohttp routes
routes = web.RouteTableDef()

@routes.get("/")
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({"status": "ok"})

async def web_server():
    """Initialize and run the web server"""
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def start_bot():
    """Start the bot"""
    await bot.start()
    print("Bot is up and running!")

async def stop_bot():
    """Stop the bot gracefully"""
    await bot.stop()
    print("Bot has stopped!")

async def main():
    """Main application logic"""
    if WEBHOOK:
        # Setup Web Server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

    # Start the bot
    await start_bot()

    # Keep the bot and server running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep loop to keep the script alive
    except (KeyboardInterrupt, SystemExit):
        await stop_bot()

# Inline Keyboard Example
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="📞 Contact", url="https://t.me/Nikhil_saini_khe"),
            InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl"),
        ],
    ]
)
# Image URLs for the random image feature
image_urls = [
    "https://tinypic.host/images/2025/02/07/IMG_20250207_224444_975.jpg",
    "https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png",
    # Add more image URLs as needed
]
# Function to format the remaining time
def format_remaining_time(expiration_datetime):
    remaining_time = expiration_datetime - datetime.now()
    days, seconds = remaining_time.days, remaining_time.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{days} Days, {hours} Hours, {minutes} Minutes"

# Function to handle subscription removal
async def check_subscriptions():
    while True:
        current_time = datetime.now()
        for user_id, details in list(authorized_users.items()):
            if details["expiration_datetime"] <= current_time:
                authorized_users.pop(user_id)
                await bot.send_message(
                    user_id,
                    "Your subscription has expired and you have been removed from the authorized users list."
                )
        await asyncio.sleep(3600)  # Check every hour
# Replace with your admin's Telegram user ID
@bot.on_message(filters.command("app") & filters.user(admins))
async def fetch_content(client, msg):
    await msg.reply("Enter your token:")
    token_msg = await client.listen(msg.chat.id)
    token = token_msg.text
    
    await msg.reply("Enter your institute name:")
    institute_name_msg = await client.listen(msg.chat.id)
    institute_name = institute_name_msg.text
    
    await msg.reply("Enter your org code:")
    org_code_msg = await client.listen(msg.chat.id)
    org_code = org_code_msg.text
    
    await msg.reply("Fetching course details...")
    course_details(token, institute_name, org_code)


@bot.on_message(filters.command("token") & filters.user(admins))
async def fetch_content(client: Client, msg: Message):
    await msg.reply("**Please enter your token:**")
    token_msg = await bot.listen(msg.chat.id)
    
    token = token_msg.text
    set_token(token)
    
    await msg.reply("**Enter your batch name:**")
    batch_msg = await bot.listen(msg.chat.id)
    
    batch_name = batch_msg.text
    await msg.reply(f"**Processing content for batch `{batch_name}`, please wait...**")

    try:
        result_file = None  # Initialize result_file before using it
        result_file = await generate_content_file(None)
        print(f"Result file: {result_file}")  # Debug print
        if result_file:
            new_file_name = f"{batch_name}.txt"
            if os.path.exists(result_file):
                os.rename(result_file, new_file_name)
                await msg.reply_document(new_file_name)
                print(f"Renamed file: {new_file_name}")  # Debug print
                # Clean up the generated file after sending it
                if os.path.exists(new_file_name):
                    os.remove(new_file_name)
                    print(f"Deleted file: {new_file_name}")  # Debug print
            else:
                await msg.reply(f"File {result_file} does not exist.")
        else:
            await msg.reply("Failed to fetch content or no content available.")
    except Exception as e:
        await msg.reply(f"An error occurred: {e}")
        print(f"An error occurred: {e}")  # Debug print

# Define the add_user command handler for admin
@bot.on_message(filters.command("add_user") & filters.user(admins))
async def add_user(client: Client, msg: Message):
    try:
        parts = msg.text.split()
        user_id = int(parts[1])
        subscription_days = int(parts[2])
        join_datetime = datetime.now()
        expiration_datetime = join_datetime + timedelta(days=subscription_days)
        
        if user_id not in authorized_users:
            authorized_users[user_id] = {
                "join_datetime": join_datetime,
                "subscription_days": subscription_days,
                "expiration_datetime": expiration_datetime
            }
            await client.send_photo(
                user_id,
                "IMG_20250218_013652_529.jpg",  # Replace with your offline image path
                caption=(
                    f"Congratulations! You have been added to the authorized users list for {subscription_days} days by {msg.from_user.mention}. 🎉\n\n"
                    f"⏰ Join Datetime : {join_datetime.strftime('%d-%m-%Y %I:%M:%S %p')}\n\n"
                    f"📅 Subscription Days : {subscription_days} Days \n\n"
                    f"⏰ Expiration DateTime : {expiration_datetime.strftime('%d-%m-%Y %I:%M:%S %p')}"
                )
            )
            await msg.reply(f"User {user_id} has been added to the authorized users list for {subscription_days} days.")
        else:
            await msg.reply(f"User {user_id} is already in the authorized users list.")
    except (IndexError, ValueError):
        await msg.reply("Usage: /add_user <user_id> <subscription_days>")

# Define the remove_user command handler for admin
@bot.on_message(filters.command("remove_user") & filters.user(admins))
async def remove_user(client: Client, msg: Message):
    try:
        user_id = int(msg.text.split()[1])
        if user_id in authorized_users:
            authorized_users.pop(user_id)
            await client.send_message(
                user_id,
                f"Sorry, you have been removed from the authorized users list by {msg.from_user.mention}."
            )
            await msg.reply(f"User {user_id} has been removed from the authorized users list.")
        else:
            await msg.reply(f"User {user_id} is not in the authorized users list.")
    except (IndexError, ValueError):
        await msg.reply("Usage: /remove_user <user_id>")


# Function to run content_fetcher.py with token and batch name


# Command to start the content fetch process
@bot.on_message(filters.command("token") & filters.user(admins))
async def fetch_content(ctx, token: str):
    set_token(token)
    await ctx.send("Processing content, please wait...")

    try:
        result_file = await generate_content_file(None)
        if result_file:
            await ctx.send("Content fetched successfully. Sending the file...")
            await ctx.send(file=discord.File(result_file))
        else:
            await ctx.send("Failed to fetch content or no content available.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

    # Clean up the generated file after sending it
    if os.path.exists(result_file):
        os.remove(result_file)



stored_org_id = None  # Scoped to this specific workflow

# Function to fetch organization details
def fetch_org_details(org_code):
    try:
        api = 'https://api.classplusapp.com/v2'
        headers = {
            'accept-encoding': 'gzip',
            'accept-language': 'EN',
            'api-version': '35',
            'app-version': '1.4.73.2',
            'connection': 'Keep-Alive',
            'content-type': 'application/json',
            'device-details': 'Xiaomi_Redmi 7_SDK-32',
            'device-id': 'c28d3cb16bbdac01',
            'host': 'api.classplusapp.com',
            'region': 'IN',
            'user-agent': 'Mobile-Android',
        }
        response = requests.get(f'{api}/orgs/{org_code}', headers=headers)
        if response.status_code == 200:
            res = response.json()
            org_id = res['data']['orgId']
            org_name = res['data'].get('orgName', 'Name not available')
            return org_name, org_id
        else:
            return None, f"Failed to fetch org details. Status Code: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"An error occurred: {e}"

# Function to fetch courses
def fetch_courses(org_id):
    try:
        decoded_value = f'{{"tutorId":null,"orgId":"{org_id}","categoryId":null}}'
        encoded_value = base64.b64encode(decoded_value.encode('utf-8')).decode('utf-8')
        base_url = f"https://api.classplusapp.com/v2/course/preview/similar/{encoded_value}"
        headers = {
            "accept": "application/json, text/plain, */*",
            "Api-Version": "22",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            courses = data.get('data', {}).get('coursesData', [])
            course_list = []
            output = "Course List:\n" + "-" * 40 + "\n"
            for idx, course in enumerate(courses, start=1):
                course_name = course.get('name', 'No Name Provided')
                batch_id = course.get('id', 'N/A')
                output += f"{idx}. {course_name} (Batch ID: {batch_id})\n"
                if batch_id != "N/A":
                    course_list.append(batch_id)
            return output, course_list
        else:
            return f"API Error: {response.status_code} - {response.text}", []
    except Exception as e:
        return f"An error occurred: {e}", []

# Function to encode courseId with orgId into Base64
def encode_course_with_base64(course_id, org_id):
    try:
        payload = {
            "courseId": course_id,
            "tutorId": None,
            "orgId": org_id,
            "categoryId": None
        }
        decoded_json = json.dumps(payload)
        encoded_value = base64.b64encode(decoded_json.encode('utf-8')).decode('utf-8')
        return encoded_value
    except Exception as e:
        return f"Error during encoding: {e}"

# `/fetchdetails` command: Org Code and Course Workflow
@bot.on_message(filters.command("fetchdetails") & filters.private)
async def fetch_details_command(_, message):
    await message.reply_text("Please send your Org Code:")

    try:
        # Wait for the user to input the Org Code
        org_code_msg = await bot.listen(message.chat.id)
        org_code = org_code_msg.text.strip()

        if not org_code:
            await message.reply_text("Error: Org Code is missing. Please provide a valid Org Code.")
            return

        # Fetch organization details
        org_name, org_id_or_error = fetch_org_details(org_code)
        if not org_name:
            await message.reply_text(f"Error: {org_id_or_error}\nPlease ensure the Org Code is correct and try again.")
            return

        await message.reply_text(f"Organization Name: {org_name}\nOrganization ID: {org_id_or_error}")

        # Fetch and display courses
        course_output, course_list = fetch_courses(org_id_or_error)
        await message.reply_text(course_output)

        # If no courses are found, stop the process here
        if not course_list:
            await message.reply_text("No courses found for this organization.")
            return

        # Ask for the Course ID
        await message.reply_text("Please send your Course ID from the course list to encode:")

        # Wait for the user to input the Course ID
        course_id_msg = await bot.listen(message.chat.id)
        course_id = course_id_msg.text.strip()

        if not course_id.isdigit():
            await message.reply_text("Invalid Course ID. Please enter a numeric Course ID.")
            return

        # Encode Course ID with Org ID
        encoded_value = encode_course_with_base64(course_id, org_id_or_error)
        if "Error" in encoded_value:
            await message.reply_text(f"Encoding failed: {encoded_value}")
            return

        # Send the encoded value back to the user
        await message.reply_text(f"Encoded value for Course ID {course_id}: {encoded_value}")

    except Exception as e:
        await message.reply_text(f"An unexpected error occurred: {e}")


        
@bot.on_message(filters.command("id"))
async def get_id(client: Client, msg: Message):
    chat_name = msg.chat.title or "Unknown"
    chat_id = msg.chat.id

    # Check if chat_id starts with 100
    if str(chat_id).startswith("100"):
        copy_text = f"/add_channel {chat_id}"
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📋 Copy Command", switch_inline_query=copy_text)]
            ]
        )
        await msg.reply(f"📃 Your Channel Name: {chat_name}\n"
                        f"🆔 Your Channel ID: {chat_id}\n\n"
                        "❌ This Chat ID is not in an Allowed Channel List\n\n"
                        "To add this Channel, use the button below to copy the command 👇",
                        reply_markup=keyboard)
        
    else:
        user_id = msg.from_user.id
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📋 Copy ID", switch_inline_query=f"**{user_id}**")],
                [InlineKeyboardButton("📥 Send Here", callback_data="send_here")]
            ]
        )
        await msg.reply(f"Your Telegram ID: {user_id}\n\n"
                        "Use the options below 👇",
                        reply_markup=keyboard)
        


# Define the add_channel command handler for admin
@bot.on_message(filters.command("add_channel") & filters.user(admins))
async def add_channel(client: Client, msg: Message):
    try:
        chat_id = int(msg.text.split()[1])
        allowed_channels.add(chat_id)
        await msg.reply(f"Channel ID {chat_id} has been added to the allowed channels list.")
    except (IndexError, ValueError):
        await msg.reply("Usage: /add_channel <channel_id>")

# Define the remove_channel command handler for admin
@bot.on_message(filters.command("remove_channel") & filters.user(admins))
async def remove_channel(client: Client, msg: Message):
    try:
        chat_id = int(msg.text.split()[1])
        if chat_id in allowed_channels:
            allowed_channels.remove(chat_id)
            await msg.reply(f"Channel ID {chat_id} has been removed from the allowed channels list.")
        else:
            await msg.reply(f"Channel ID {chat_id} is not in the allowed channels list.")
    except (IndexError, ValueError):
        await msg.reply("Usage: /remove_channel <channel_id>")

# Start the bot
async def main():
    await check_subscriptions()






class Data:
    START = (
        "🌟 Welcome {0}! 🌟\n\n"
    )
# Define the start command handler
@bot.on_message(filters.command("start"))
async def start(client: Client, msg: Message):
    user = await client.get_me()
    mention = user.mention
    start_message = await client.send_message(
        msg.chat.id,
        Data.START.format(msg.from_user.mention)
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Initializing Uploader bot... 🤖\n\n"
        "Progress: [⬜⬜⬜⬜⬜⬜⬜⬜⬜] 0%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Loading features... ⏳\n\n"
        "Progress: [🟥🟥🟥⬜⬜⬜⬜⬜⬜] 25%\n\n"
    )
    
    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "This may take a moment, sit back and relax! 😊\n\n"
        "Progress: [🟧🟧🟧🟧🟧⬜⬜⬜⬜] 50%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Checking subscription status... 🔍\n\n"
        "Progress: [🟨🟨🟨🟨🟨🟨🟨⬜⬜] 75%\n\n"
    )

    await asyncio.sleep(1)
    if msg.from_user.id in authorized_users:
        details = authorized_users[msg.from_user.id]
        join_datetime = details["join_datetime"]
        subscription_days = details["subscription_days"]
        expiration_datetime = details["expiration_datetime"]
        remaining_time = format_remaining_time(expiration_datetime)

        offline_image_path = "IMG_20250218_013652_529.jpg"  # Replace with your offline image path
        await client.send_photo(
            msg.chat.id,
            offline_image_path,
            caption=(
                f"Great! You are a 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 member!\n\n  🌟 Welcome {msg.from_user.mention} ! 👋\n\n"
                f"⏰ Join Datetime : {join_datetime.strftime('%d-%m-%Y %I:%M:%S %p')}\n\n"
                f"📅 Subscription Days : {subscription_days} Days \n\n"
                f"⏰ Expiration DateTime : {expiration_datetime.strftime('%d-%m-%Y %I:%M:%S %p')}\n\n"
                f"⌛️Remaining Time : {remaining_time}\n\n"
                "I Am A Bot For Download Links From Your **🌟.TXT 🌟** File And Then Upload That File On Telegram."
                " So Basically If You Want To Use Me First Send Me /drm Command And Then Follow Few Steps..\n\n"
                "**├── Bot Made By : **『 🅹🅰️🅸 🆂🅷🆁🅸 🆁🅰️🅼 ⚡️ 🧑‍💻』**\n\n"
                "Use /stop to stop any ongoing task."
            ),
            reply_markup=help_button_keyboard
        )
    else:
        offline_image_path = "IMG_20250218_015150_501.jpg"  # Replace with your offline image path
        await client.send_photo(
            msg.chat.id,
            offline_image_path,
            caption=(
                f"  🌟 Welcome {msg.from_user.mention} ! 👋\n\n"
                "You are currently using the 𝗙𝗥𝗘𝗘 version. 🆓\n\n"
                "I'm here to make your life easier by downloading videos from your **.txt** file 📄 and uploading them directly to Telegram!\n\n"
                "Want to get started? Your id\n\n"
                "💬 Contact @Course_diploma_bot to get the 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 🎫 and unlock the full potential of your new bot! 🔓"
            )
        )

# 


# Start the 
    

# Start the bot

    

# Start the 


# Start the bot


# Start the bot
    

# Add this at the end to run the bot


# Add this at the end to run the bot







@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):
    if m.from_user.id not in authorized_users:
        await m.reply_text("Sorry, you are not eligible.")
        return

    # Save authorized users to a file before stopping
    save_authorized_users()

    await m.reply_text("**Stopped** 🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)  # Restart the bot


# Define the drm command handler
@bot.on_message(filters.command(["drm"]))
async def upload(bot: Client, m: Message):
    if m.from_user.id not in authorized_users:
        await m.reply_text("Sorry, you are not eligible.")
        return

    editable = await m.reply_text('➠ 𝐒𝐞𝐧𝐝 𝐌𝐞 𝐘𝐨𝐮𝐫 𝐓𝐗𝐓 𝐅𝐢𝐥𝐞 𝐢𝐧 𝐀 𝐏𝐫𝐨𝐩𝐞𝐫 𝐖𝐚𝐲 **\n\n**├── Bot Made By : **『 🅹🅰️🅸 🆂🅷🆁🅸 🆁🅰️🅼 ⚡️ 🧑‍💻』**')
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)

    path = f"./downloads/{m.chat.id}"

    try:
        # Extract the file name without extension
        file_name = os.path.basename(x)  # Get the file name from the path
        raw_text0 = os.path.splitext(file_name)[0]  # Remove the file extension

        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))

        # Print or use raw_text0 for further processing
        print(f"Extracted file name: {raw_text0}")

        # Continue with the rest of the logic
        # (e.g., processing links, etc.)

        # Clean up the downloaded file
        os.remove(x)

    except Exception as e:
        await m.reply_text(f"**∝ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐟𝐢𝐥𝐞 𝐢𝐧𝐩𝐮𝐭 𝐨𝐫 𝐞𝐫𝐫𝐨𝐫: {str(e)}**")
        os.remove(x)
        return



    
   
    await editable.edit(f"**Total Number of 🔗 Links found are** **{len(links)}**\n**├─ 📽️ Video Links :**\n**├─ 📑 PDF Links :**\n**├─ 🖼️ Image Links :**\n**├─ 🔗 Other Links:**\n\n**Send From where You want to 📩 Download\n**Initial is  :** **1**\n\n **├── Bot Made By : **『 🅹🅰️🅸 🆂🅷🆁🅸 🆁🅰️🅼 ⚡️ 🧑‍💻』**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**∝ 𝐍𝐨𝐰 𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐞𝐧𝐝 𝐌𝐞 𝐘𝐨𝐮𝐫 𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞**")
    input1: Message = await bot.listen(editable.chat.id)
    
    # Check if the input is "C" to copy from raw_text0
    if input1.text.strip().lower() == "c":
        raw_text0 = raw_text0  # Use the existing value of raw_text0
    else:
        raw_text0 = input1.text  # Use the user's input
    
    await input1.delete(True)

    await editable.edit("**Enter Resolution 🎞️ : **\n\n**144**\n**240**\n**360**\n**480**\n**720**\n**1080**\n\n**please choose quality**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
    
    

    await editable.edit("Enter 🌟 Extracted name  or send \n\n 📄 You can also specify a custom name \n\n   『 🅹🅰️🅸 🆂🅷🆁🅸 🆁🅰️🅼 ⚡️ 🧑‍💻』 ")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    highlighter  = f"️ ⁪⁬⁮⁮⁮"
    if raw_text3 == 'Robin':
        MR = highlighter 
    else:
        MR = raw_text3
    await editable.edit("**𝗘𝗻𝘁𝗲𝗿 𝗣𝘄 𝗧𝗼𝗸𝗲𝗻 𝗙𝗼𝗿 𝗣𝘄 𝗨𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗼𝗿 𝗦𝗲𝗻𝗱 `'noo'` 𝗙𝗼𝗿 𝗢𝘁𝗵𝗲𝗿𝘀**")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)
    if raw_text4 == 'noo':
        MR = token
    else:
        MR = raw_text4
   
    await editable.edit("⚪Send   ☞ `no` for **video** format\n\n🔘Send   ☞ `No` for **Document** format")
    input6 = message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb == "no"

    await m.reply_text(
        f"<pre><code>**🎯Target Batch :** `{raw_text0}`</code></pre>"
    )

    count =int(raw_text)   
    try:
        for i in range(count - 1, len(links)):

            V = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","") # .replace("mpd","m3u8")
            url = "https://" + V

            if "tencdn.classplusapp" in url:
                headers = {'Host': 'api.classplusapp.com', 'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                params = (('url', f'{url}'),)
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  

          
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or '4b06bf8d61c41f8310af9b2624459378203740932b456b07fcf817b737fbae27' in url:
                headers = { 'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9',"X-CDN-Tag": "empty"}
                response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                url   = response.json()['url']
            elif 'media-cdn' in url or 'webvideos' in url or 'drmcdni' in url:
             url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9'}).json()['url']
            elif 'cpvod' in url or 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url:
             url = requests.get(f'http://api.masterapi.tech/akamai-player-v3?url={url}', headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'}).json()['url']
             url0 = f"https://dragoapi.vercel.app/video/{url}"  
            elif "appx" in url:
             

                
        
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                    
                elif 'Key-Pair-Id' in url:
                    url = None
                    
                elif '.m3u8' in url:
                    url =f"https://m3u8play.dev/?url={url}"
            
                elif '/utkarsha' in url:
                    id = url.split("/")[-2]
                    url = f"https://apps-s3-prod.utkarshapp.com/admin_v1/file_library/videos/enc_plain_mp4/{id}/plain/{{res}}.mp4"
                
                
            if "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
            elif "/khansirvod4" and "akamaized" in url:
              url = url.replace(url.split("/")[-1], raw_text2+".m3u8")
                         
            elif "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
                url = url.split("bcov_auth")[0]+bcov

            elif '/master.mpd' in url:
             id =  url.split("/")[-2]
             url =  f"https://madxapi-d0cbf6ac738c.herokuapp.com/{id}/master.m3u8?token={raw_text4}"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'
            if "youtu" in url:
              ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba[ext=m4a]/b[ext=mp4]"
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            
            elif "m3u8" or "livestream" in url:
                cmd = f'yt-dlp -f "{ytf}" --no-keep-video --remux-video mkv "{url}" -o "{name}.%(ext)s"'

            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:  
                
                cc = f'**——— ✦ ** {str(count).zfill(3)}.**——— ✦ ** \n\n** 🎞️ Title :**{𝗻𝗮𝗺𝗲𝟭}\n**├── Extention : @Course_diploma_bot.mkv**\n**├── Resolution : {res}**\n\n<pre><code>📚𝐂𝐨𝐮𝐫𝐬𝐞 » {raw_text0}</code></pre>\n\n**🌟 Extracted By** **{raw_text3}**'
                cc1 = f'**——— ✦ ** {str(count).zfill(3)}.**——— ✦ **\n\n**📁 Title  :** {𝗻𝗮𝗺𝗲𝟭}\n**├── Extention : @Course_diploma_bot.pdf**\n\n<pre><code>📚𝐂𝐨𝐮𝐫𝐬𝐞 » {raw_text0}</code></pre>\n\n**🌟 Extracted By** **{raw_text3}**'
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count+=1
                        continue

                elif ".pdf*" in url:
                    try:
                        url_part, key_part = url.split("*")
                        url = f"https://dragoapi.vercel.app/pdf/{url_part}*{key_part}"
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count += 1
                        continue   

                elif ".pdf" in url:
                    try:
                        await asyncio.sleep(4)
                        url = url.replace(" ", "%20")
                        scraper = cloudscraper.create_scraper()
                        response = scraper.get(url)
                        if response.status_code == 200:
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)
                            await asyncio.sleep(4)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        else:
                            await m.reply_text(f"Failed to download PDF: {response.status_code} {response.reason}")
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count += 1
                        continue

                elif "adda247" in url:
                    try:
                         # Extract the file extension from the URL (e.g., .doc, .pdf)
                        response = requests.get(url, headers={
                            "Host": "store.adda247.com",  # Create output file name
                            "User-Agent": "Mozilla/5.0 (Linux; Android 11; moto g(40) fusion Build/RRI31.Q1-42-51-8; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36",
                            "accept": "*/*",
                            "x-requested-with": "com.adda247.app",
                            "sec-fetch-site": "same-origin",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-dest": "empty",
                            "referer": "https://store.adda247.com/build/pdf.worker.js",
                            "accept-encoding": "gzip, deflate",
                            "accept-language": "en-US,en;q=0.9",
                            "cookie": f"cp_token={raw_text4}"
                         }, stream=True)
                         # Check response
                        if response.status_code == 200:
                            file_extension = url.split(".")[-1]  # Extract file extension
                            output_file = f"{name}.{file_extension}"  # Save with appropriate file extension
                            # Save file locally
                            with open(output_file, "wb") as f:
                                for chunk in response.iter_content(chunk_size=1024):
                                        f.write(chunk)
                         # Send the document
                            await bot.send_document(chat_id=m.chat.id, document=output_file, caption=cc1)
                            count += 1
                         # Cleanup after sending
                            os.remove(output_file)
                            time.sleep(2)
                    except Exception as e:
                        await m.reply_text(
                        f"{e}\nDownload Failed\n\nName : {name}\n\nLink : {url}"
                 )
                        pass
                elif ".pdf" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count += 1
                        continue


                elif ".zip" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.zip" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.zip', caption=cczip)
                        count += 1
                        os.remove(f'{name}.zip')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count += 1
                        continue

                elif ".jpg" in url or ".png" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.jpg" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=m.chat.id, document=f'{name}.jpg', caption=ccimg)
                        count += 1
                        os.remove(f'{name}.jpg')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count += 1
                        continue
                else:
                    emoji_message = await show_random_emojis(message)
                    progress_percent = (count / len(links)) * 100
                    Show = f"**🚀 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 = {progress_percent:.2f}%  🚀... »**\n\n**├──🎞️ 📊 Total Links = {len(links)}**\n\n**├──🎞️ ⚡️ Currently On = {str(count).zfill(3)}**\n\n**├──🎞️ 🔥 Remaining Links = {len(links) - count}**\n\n**├──🎞️ 📈 Progress = {progress_percent:.2f}% **\n\n**├──🎞️ Title** {name}\n\n**├── Resolution {raw_text2}**\n\n**├── Url : ** `Time Gya Url Dekhne ka 😅`\n\n**├── Bot Made By : **『 🅹🅰️🅸 🆂🅷🆁🅸 🆁🅰️🅼 ⚡️ 🧑‍💻』"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await emoji_message.delete()
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"**downloading Interupted **\n{str(e)}\n**Name** » {name}\n**Link** » `{url}`"
                )
                continue

    
    except Exception as e:
        await m.reply_text(e)
    await m.reply_text(f"⋅ ─ list index (**{str(count).zfill(3)}**-**{len(links) - count}**) out of range ─ ⋅\n\n"
                   f"✨ **BATCH** » {raw_text0} ✨\n\n"
                   f"⋅ ─ DOWNLOADING ✩ COMPLETED ─ .")
    await m.reply_text("**That's It ❤️**")


bot.run()
if __name__ == "__main__":
    asyncio.run(main())
