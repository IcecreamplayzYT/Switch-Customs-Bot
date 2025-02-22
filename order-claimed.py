import discord
from discord import app_commands
from discord.ext import commands

# Role & Channel IDs
DESIGNER_ROLE_ID = 1342201759111712799  # Designer role (Temporairily changed for testing 1342201759111712799 is actual id)
ORDER_LOG_CHANNEL_ID = 1342230845032894514  # Order log channel (to be changed)

class ClaimOrder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="claim", description="Claim an order as a designer.")
    @app_commands.describe(order_id="The ID of the order you are claiming.")
    async def claim(self, interaction: discord.Interaction, order_id: str):
        """Claim an order and log it."""

        # Check if user has the Designer role
        if not any(role.id == DESIGNER_ROLE_ID for role in interaction.user.roles):
            return await interaction.response.send_message("❌ You must be a **Designer** to claim an order.", ephemeral=True)

        # Fetch logging channel
        log_channel = interaction.guild.get_channel(ORDER_LOG_CHANNEL_ID)
        if not log_channel:
            return await interaction.response.send_message("⚠️ Order log channel not found.", ephemeral=True)

        # Order channel link
        order_channel_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}"
        order_channel_name = interaction.channel.name

        # Create the claim embed
        embed = discord.Embed(title="✅ Order Claimed", color=discord.Color.green())
        embed.add_field(name="Order ID", value=order_id, inline=False)
        embed.add_field(name="Claimed By", value=interaction.user.mention, inline=False)
        embed.add_field(name="Channel", value=f"#{order_channel_name}", inline=False)
        embed.set_footer(text="Order has been claimed successfully.")

        # Send embed in the current channel
        await interaction.response.send_message(embed=embed)

        # Log the claim in the order log channel
        claim_message = f"📢 **Order Claimed**: {interaction.user.mention} claimed **Order {order_id}** in [#{order_channel_name}]({order_channel_link})."
        await log_channel.send(claim_message)

# Setup function for bot to load the cog
async def setup(bot):
    await bot.add_cog(ClaimOrder(bot))