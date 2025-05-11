from discord.ext import commands
from discord import app_commands
import discord
from firebase_db import db

class SearchCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="search", description="Search for a media title (fuzzy match)")
    @app_commands.describe(query="Search query, partial name")
    async def search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        try:
            guild_id = str(interaction.guild_id)
            media_docs = db.collection("guilds").document(guild_id).collection("media").stream()

            results = []
            for doc in media_docs:
                data = doc.to_dict()
                if query.lower() in data.get("title", "").lower():
                    reviews = list(db.collection("guilds").document(guild_id).collection("media").document(doc.id).collection("reviews").stream())
                    ratings = [r.to_dict().get("rating", 0) for r in reviews]
                    if ratings:
                        avg = sum(ratings) / len(ratings)
                        results.append((data["title"], data["category"], avg, len(ratings)))

            if not results:
                await interaction.followup.send("🔍 No results found.", ephemeral=True)
                return

            msg = "**🔎 Search Results**\n\n"
            for title, category, avg, count in sorted(results, key=lambda x: x[3], reverse=True)[:10]:
                msg += f"• **{title}** ({category}) — ⭐ {avg:.2f}/10 from {count} review(s)\n"

            await interaction.followup.send(msg)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SearchCommand(bot))
