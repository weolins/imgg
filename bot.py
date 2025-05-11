import os
import threading
import asyncio
from dotenv import load_dotenv
from flask import Flask

# === Load environment variables ===
load_dotenv()

# === Start Flask web server ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Im.gg Discord bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

# === Start Discord Bot ===
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s) globally.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

async def main():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'commands.{filename[:-3]}')
    await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
