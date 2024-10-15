import telebot
import m3u8
import subprocess
import os
import requests
import time

API_TOKEN = 'YOUR_BOT_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

# Path to save recorded videos
RECORDING_PATH = "./recordings/"
if not os.path.exists(RECORDING_PATH):
    os.makedirs(RECORDING_PATH)

# Start command
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Welcome! Send me an m3u8 stream URL to start recording.")

# Handle m3u8 URL input
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def handle_m3u8_url(message):
    bot.send_message(message.chat.id, "Set recording quality (e.g., 720p, 480p, etc.):")
    bot.register_next_step_handler(message, set_quality, message.text)

# Set recording quality
def set_quality(message, url):
    quality = message.text
    bot.send_message(message.chat.id, "Set recording duration (in seconds):")
    bot.register_next_step_handler(message, set_duration, url, quality)

# Set recording duration and start recording
def set_duration(message, url, quality):
    try:
        duration = int(message.text)
        bot.send_message(message.chat.id, "Recording started...")

        # Create file path for recorded video
        timestamp = str(int(time.time()))
        output_file = f"{RECORDING_PATH}{timestamp}_{quality}.mp4"

        # Start recording using ffmpeg
        record_stream(url, output_file, duration, quality)

        # Send recorded video to Telegram
        with open(output_file, 'rb') as video:
            bot.send_video(message.chat.id, video)

        bot.send_message(message.chat.id, "Recording complete!")

    except ValueError:
        bot.send_message(message.chat.id, "Invalid duration. Please provide the duration in seconds.")

# Function to record video using ffmpeg
def record_stream(url, output_file, duration, quality):
    command = [
        "ffmpeg",
        "-i", url,
        "-t", str(duration),
        "-s", quality,
        "-c", "copy",  # to maintain stream copy and quality
        output_file
    ]
    subprocess.run(command)

# Polling to keep the bot running
bot.polling()
