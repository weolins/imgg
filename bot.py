import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

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
    await bot.start(os.getenv("BOT_TOKEN")) # Replace with your bot token

if __name__ == "__main__":
    asyncio.run(main())
