from discord.ext import commands
from discord import app_commands
import discord
from firebase_db import db
from firebase_admin import firestore
from utils import normalize_title

CATEGORY_CHOICES = [
    app_commands.Choice(name="Movie", value="movie"),
    app_commands.Choice(name="Book", value="book"),
    app_commands.Choice(name="TV Show", value="tv show"),
    app_commands.Choice(name="Game", value="game"),
    app_commands.Choice(name="Other", value="other"),
]

class RateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rate", description="Rate a piece of media (1–10)")
    @app_commands.choices(category=CATEGORY_CHOICES)
    @app_commands.describe(
        title="Media title (e.g., Avengers Endgame)",
        category="Category",
        rating="Your rating from 1 to 10",
        comment="Optional comment"
    )
    async def rate(self, interaction: discord.Interaction, title: str, category: app_commands.Choice[str], rating: int, comment: str = None):
        await interaction.response.defer(thinking=True)

        try:
            guild_id = str(interaction.guild_id)
            user_id = str(interaction.user.id)
            normalized = normalize_title(title)

            media_ref = db.collection("guilds").document(guild_id).collection("media").document(normalized)
            media_ref.set({
                "title": title.strip(),
                "normalized_title": normalized,
                "category": category.value
            }, merge=True)

            media_ref.collection("reviews").add({
                "user_id": user_id,
                "rating": rating,
                "comment": comment,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

            response = f"✅ **{interaction.user.display_name}** rated **{title}** ({category.name}) a **{rating}/10**"
            if comment:
                response += f"\n💬 _{comment}_"

            await interaction.followup.send(response)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RateCommand(bot))
