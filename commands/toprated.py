import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from firebase_db import db
from firebase_admin import firestore

from discord.ext import commands
from discord import app_commands
import discord

CATEGORY_CHOICES = [
    app_commands.Choice(name="All", value=""),
    app_commands.Choice(name="Movie", value="movie"),
    app_commands.Choice(name="Book", value="book"),
    app_commands.Choice(name="TV Show", value="tv show"),
    app_commands.Choice(name="Game", value="game"),
    app_commands.Choice(name="Other", value="other"),
]

class TopRatedCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="toprated", description="See top-rated media")
    @app_commands.choices(category=CATEGORY_CHOICES)
    @app_commands.describe(category="Choose a category or see all")
    async def toprated(self, interaction: discord.Interaction, category: app_commands.Choice[str]):
        await interaction.response.defer()

        try:
            guild_id = str(interaction.guild_id)
            selected_cat = category.value
            media_docs = db.collection("guilds").document(guild_id).collection("media").stream()

            results = []
            for doc in media_docs:
                data = doc.to_dict()
                if selected_cat and data.get("category") != selected_cat:
                    continue

                reviews = list(doc.reference.collection("reviews").stream())
                ratings = [r.to_dict().get("rating", 0) for r in reviews]
                if len(ratings) >= 2:
                    avg = sum(ratings) / len(ratings)
                    results.append((data["title"], data["category"], avg, len(ratings)))

            if not results:
                await interaction.followup.send("ℹ️ No media found with enough reviews.", ephemeral=True)
                return

            msg = "**Top-Rated Media**\n\n"
            for title, cat, avg, count in sorted(results, key=lambda x: x[2], reverse=True)[:10]:
                msg += f"**{title}** ({cat}) — ⭐ {avg:.2f}/10 from {count} reviews\n"

            await interaction.followup.send(msg)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TopRatedCommand(bot))
