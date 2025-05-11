import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from firebase_db import db

from discord.ext import commands
from discord import app_commands
import discord
from utils import normalize_title

CATEGORY_CHOICES = [
    app_commands.Choice(name="Movie", value="movie"),
    app_commands.Choice(name="Book", value="book"),
    app_commands.Choice(name="TV Show", value="tv show"),
    app_commands.Choice(name="Game", value="game"),
    app_commands.Choice(name="Other", value="other"),
]

class ReviewsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reviews", description="See all reviews for a media item")
    @app_commands.choices(category=CATEGORY_CHOICES)
    @app_commands.describe(
        title="Exact title of the media",
        category="Category"
    )
    async def reviews(self, interaction: discord.Interaction, title: str, category: app_commands.Choice[str]):
        await interaction.response.defer()

        try:
            guild_id = str(interaction.guild_id)
            normalized = normalize_title(title)

            media_ref = db.collection("guilds").document(guild_id).collection("media").document(normalized)
            media_doc = media_ref.get()

            if not media_doc.exists or media_doc.to_dict().get("category") != category.value:
                await interaction.followup.send("❌ No media found with that title and category.", ephemeral=True)
                return

            reviews = list(media_ref.collection("reviews").stream())
            if not reviews:
                await interaction.followup.send("ℹ️ No reviews found for that item.", ephemeral=True)
                return

            ratings = [r.to_dict().get("rating", 0) for r in reviews]
            avg = sum(ratings) / len(ratings)
            count = len(ratings)

            header = f"📖 **{title}** ({category.name}) — ⭐ {avg:.2f}/10 from {count} review(s)\n\n"
            body = ""
            for r in reviews[:10]:
                data = r.to_dict()
                user = await interaction.client.fetch_user(int(data["user_id"]))
                body += f"**{user.display_name}** — {data['rating']}/10"
                if data.get("comment"):
                    body += f"\n> {data['comment']}"
                body += "\n\n"

            await interaction.followup.send(header + body)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReviewsCommand(bot))
