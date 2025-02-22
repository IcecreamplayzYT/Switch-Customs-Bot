import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# Channel IDs
QC_CHANNEL_ID = 1342233279050416129  # Quality Control channel
QC_RESULTS_CHANNEL_ID = 1342224308793114705  # Channel where results (approvals/denials) are sent

# Role ID
DESIGNER_ROLE_ID = 1342201759111712799  # Designer role

class QualityControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="control", description="Submit a design for quality control (Designers only).")
    async def control(self, interaction: discord.Interaction, order_id: str, designer: discord.Member):
        """Only Designers can submit a design for quality control."""
        
        # Restrict to Designer role
        if not any(role.id == DESIGNER_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ You must be a **Designer** to use this command.", ephemeral=True)
            return
        
        # Open an image upload modal
        await interaction.response.send_modal(QCImageUpload(order_id, designer))

class QCImageUpload(discord.ui.Modal, title="Upload QC Images"):
    def __init__(self, order_id, designer):
        super().__init__()
        self.order_id = order_id
        self.designer = designer

    images = discord.ui.TextInput(label="Image Links", placeholder="Paste image URLs (separate multiple links with a comma)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        """Handles image submissions and sends the embed to QC channel."""

        # Split multiple image links
        image_urls = [url.strip() for url in self.images.value.split(",") if url.strip()]
        if not image_urls:
            await interaction.response.send_message("❌ You must provide at least one valid image URL.", ephemeral=True)
            return

        # Fetch QC channel
        qc_channel = interaction.guild.get_channel(QC_CHANNEL_ID)
        if not qc_channel:
            await interaction.response.send_message("❌ Quality Control channel not found.", ephemeral=True)
            return

        # Create QC submission embed
        embed = discord.Embed(title="🛠️ Quality Control Submission", color=discord.Color.blue())
        embed.add_field(name="🆔 Order ID", value=self.order_id, inline=True)
        embed.add_field(name="👤 Designer", value=self.designer.mention, inline=True)
        embed.add_field(name="📅 Submitted On", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=False)
        embed.set_image(url=image_urls[0])  # Show first image

        # Add Approve/Deny buttons
        view = QCApprovalView(self.designer, self.order_id, interaction.client)

        # Send embed to QC channel
        await qc_channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Your submission has been sent for Quality Control.", ephemeral=True)

class QCApprovalView(discord.ui.View):
    def __init__(self, designer, order_id, bot):
        super().__init__(timeout=None)
        self.designer = designer
        self.order_id = order_id
        self.bot = bot

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Edit the original message to show it was approved
        await interaction.message.edit(embed=interaction.message.embeds[0].set_footer(text="✅ Approved"), view=None)

        # Fetch QC Results channel
        results_channel = interaction.guild.get_channel(QC_RESULTS_CHANNEL_ID)
        if results_channel:
            await results_channel.send(f"✅ {self.designer.mention} **Your product has passed Quality Control!** 🎉")

        await interaction.response.send_message("✅ Design approved.", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = QCDenyModal(self.designer, self.order_id, interaction.message, self.bot)
        await interaction.response.send_modal(modal)

class QCDenyModal(discord.ui.Modal, title="Deny Quality Check Submission"):
    reason = discord.ui.TextInput(label="Denial Reason", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, designer, order_id, message, bot):
        super().__init__()
        self.designer = designer
        self.order_id = order_id
        self.message = message
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        embed = self.message.embeds[0]
        embed.set_footer(text=f"❌ Denied - Reason: {self.reason.value}")

        # Edit the original message to show it was denied
        await self.message.edit(embed=embed, view=None)

        # Fetch QC Results channel
        results_channel = interaction.guild.get_channel(QC_RESULTS_CHANNEL_ID)
        if results_channel:
            await results_channel.send(f"{self.designer.mention} ❌ Product was Denied, Quality does not meet standards Expected.")

            # Send Denial Embed
            denial_embed = discord.Embed(title="❌ Quality Check Denied", color=discord.Color.red())
            denial_embed.add_field(name="Reason", value=self.reason.value, inline=False)
            await results_channel.send(embed=denial_embed)

        await interaction.response.send_message("✅ Denial reason sent.", ephemeral=True)

# Setup function for bot to load the cog
async def setup(bot):
    await bot.add_cog(QualityControl(bot))