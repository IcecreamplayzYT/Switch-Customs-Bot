import discord
from discord import app_commands
from discord.ext import commands

class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        """Replies with Pong! and bot latency."""
        latency = round(self.bot.latency * 1000)  # Convert to ms
        await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms", ephemeral=True)

# 🔹 Fix: Add the setup function
async def setup(bot):
    await bot.add_cog(PingCommand(bot))