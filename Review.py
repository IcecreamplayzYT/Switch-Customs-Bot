import discord
from discord import app_commands
from discord.ext import commands

# Review Channel ID
REVIEW_CHANNEL_ID = 1342201735992840242  # Update with correct channel ID

class ReviewCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="review", description="Submit a review for a designer.")
    @app_commands.describe(designer="Select the designer", reviewer="Select yourself (the reviewer)", notes="Add any additional comments")
    async def review(self, interaction: discord.Interaction, designer: discord.Member, reviewer: discord.Member, notes: str = "No additional notes provided."):
        """Starts the review process by opening a dropdown for product type."""
        view = ReviewDropdown(self.bot, designer, reviewer, notes)
        await interaction.response.send_message("📌 Select the product type:", view=view, ephemeral=True)

class ReviewDropdown(discord.ui.View):
    def __init__(self, bot, designer, reviewer, notes):
        super().__init__(timeout=None)
        self.bot = bot
        self.designer = designer
        self.reviewer = reviewer
        self.notes = notes

    @discord.ui.select(
        placeholder="Select Product Type",
        options=[
            discord.SelectOption(label="Livery", emoji="🎨"),
            discord.SelectOption(label="ELS", emoji="🚔"),
            discord.SelectOption(label="Discord", emoji="💻"),
            discord.SelectOption(label="Clothing", emoji="👕"),
            discord.SelectOption(label="Graphics", emoji="🖼️")
        ]
    )
    async def select_product(self, interaction: discord.Interaction, select: discord.ui.Select):
        product = select.values[0]
        view = ReviewStars(self.bot, self.designer, self.reviewer, product, self.notes)
        await interaction.response.send_message(f"📌 You selected **{product}**. Now choose a star rating:", view=view, ephemeral=True)

class ReviewStars(discord.ui.View):
    def __init__(self, bot, designer, reviewer, product, notes):
        super().__init__(timeout=None)
        self.bot = bot
        self.designer = designer
        self.reviewer = reviewer
        self.product = product
        self.notes = notes

    @discord.ui.select(
        placeholder="Select Star Rating",
        options=[
            discord.SelectOption(label="⭐", value="1"),
            discord.SelectOption(label="⭐⭐", value="2"),
            discord.SelectOption(label="⭐⭐⭐", value="3"),
            discord.SelectOption(label="⭐⭐⭐⭐", value="4"),
            discord.SelectOption(label="⭐⭐⭐⭐⭐", value="5"),
        ]
    )
    async def select_stars(self, interaction: discord.Interaction, select: discord.ui.Select):
        stars = select.values[0]

        # Create Review Embed
        embed = discord.Embed(title="🌟 New Review Submitted", color=discord.Color.gold())
        embed.add_field(name="👤 Designer", value=self.designer.mention, inline=True)
        embed.add_field(name="📝 Reviewer", value=self.reviewer.mention, inline=True)
        embed.add_field(name="📌 Product Type", value=self.product, inline=False)
        embed.add_field(name="⭐ Rating", value=stars, inline=True)
        embed.add_field(name="🗒️ Notes", value=self.notes, inline=False)

        # Send Embed to Review Channel
        review_channel = self.bot.get_channel(REVIEW_CHANNEL_ID)
        if review_channel:
            await review_channel.send(embed=embed)
            await interaction.response.send_message("✅ Review submitted successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Review channel not found.", ephemeral=True)

# Setup function for bot to load the cog
async def setup(bot):
    await bot.add_cog(ReviewCommand(bot))