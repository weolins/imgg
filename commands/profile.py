from discord.ext import commands
from discord import app_commands
import discord
from firebase_db import db

class ProfileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="See your own review stats")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            guild_id = str(interaction.guild_id)
            user_id = str(interaction.user.id)
            media_docs = db.collection("guilds").document(guild_id).collection("media").stream()

            all_ratings = []
            for media in media_docs:
                reviews = media.reference.collection("reviews").where("user_id", "==", user_id).stream()
                for r in reviews:
                    all_ratings.append(r.to_dict().get("rating", 0))

            if not all_ratings:
                await interaction.followup.send("You haven't reviewed anything yet!", ephemeral=True)
                return

            avg = sum(all_ratings) / len(all_ratings)
            await interaction.followup.send(
                f"📊 **{interaction.user.display_name}'s Profile**\n"
                f"• Total reviews: **{len(all_ratings)}**\n"
                f"• Average rating: **{avg:.2f}/10**"
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ProfileCommand(bot))
