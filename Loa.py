import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta

# Role & Channel IDs
LOA_ROLE_ID = 1342882515676827668  # LOA Role ID
DESIGNING_TEAM_ROLE_ID = 1342201759111712799  # Only Designers can approve LOA
APPROVAL_CHANNEL_ID = 1342883804896821270  # Channel where requests are sent
SERVER_ICON_URL = "https://cdn.discordapp.com/icons/1342198087933755555/your_server_icon.png"  # Update with actual URL

class LOARequest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="loa", description="Request a Leave of Absence (LOA).")
    async def loa(self, interaction: discord.Interaction, duration: str, reason: str):
        """Handles LOA requests, sends them for approval, and processes responses."""

        # Validate duration format (e.g., 5d, 2m, 1y)
        unit = duration[-1].lower()
        if unit not in ["d", "m", "y"] or not duration[:-1].isdigit():
            await interaction.response.send_message("❌ Invalid format! Use `d` for days, `m` for months, or `y` for years. Example: `5d`", ephemeral=True)
            return
        
        amount = int(duration[:-1])
        today = datetime.utcnow()
        
        if unit == "d":
            end_date = today + timedelta(days=amount)
        elif unit == "m":
            end_date = today + timedelta(days=amount * 31)
        elif unit == "y":
            end_date = today + timedelta(days=amount * 365)

        # Convert to Discord timestamp
        request_time = f"<t:{int(today.timestamp())}:F>"
        end_time = f"<t:{int(end_date.timestamp())}:F>"

        # Create approval embed
        embed = discord.Embed(title="📝 LOA Request", color=discord.Color.orange())
        embed.add_field(name="Requester", value=interaction.user.mention, inline=True)
        embed.add_field(name="Duration", value=f"{duration} (Until {end_time})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Requested On", value=request_time, inline=True)

        # Add approval buttons
        view = LOAApprovalView(interaction.user, reason, duration, end_time, self.bot)

        # Send to approval channel
        channel = self.bot.get_channel(APPROVAL_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message("✅ Your LOA request has been submitted for approval.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Failed to find the approval channel.", ephemeral=True)

class LOAApprovalView(discord.ui.View):
    def __init__(self, requester, reason, duration, end_time, bot):
        super().__init__(timeout=None)
        self.requester = requester
        self.reason = reason
        self.duration = duration
        self.end_time = end_time
        self.bot = bot

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has the Designing Team role
        if not any(role.id == DESIGNING_TEAM_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to approve LOAs.", ephemeral=True)
            return
        
        # Assign LOA Role
        try:
            loa_role = interaction.guild.get_role(LOA_ROLE_ID)
            if loa_role:
                await self.requester.add_roles(loa_role)
        except Exception as e:
            print(f"❌ Failed to assign LOA role: {e}")

        # Send DM
        embed = discord.Embed(title="✅ LOA Approved", color=discord.Color.green())
        embed.set_thumbnail(url=SERVER_ICON_URL)
        embed.add_field(name="Your LOA has been approved!", value=f"Your leave of absence until {self.end_time} has been approved.", inline=False)
        embed.set_footer(text="Enjoy your time off!")

        try:
            await self.requester.send(embed=embed)
        except:
            pass

        await interaction.message.edit(embed=interaction.message.embeds[0].set_footer(text="✅ Approved"), view=None)
        await interaction.response.send_message("✅ LOA request approved.", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == DESIGNING_TEAM_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ You do not have permission to deny LOAs.", ephemeral=True)
            return

        modal = LOADenyModal(self.requester, interaction.message)
        await interaction.response.send_modal(modal)

class LOADenyModal(discord.ui.Modal, title="Deny LOA Request"):
    reason = discord.ui.TextInput(label="Denial Reason", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, requester, message):
        super().__init__()
        self.requester = requester
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        embed = self.message.embeds[0]
        embed.set_footer(text=f"❌ Denied - Reason: {self.reason.value}")

        await self.message.edit(embed=embed, view=None)

        # Send DM to user
        embed_dm = discord.Embed(title="❌ LOA Denied", color=discord.Color.red())
        embed_dm.set_thumbnail(url=SERVER_ICON_URL)
        embed_dm.add_field(name="Your LOA request has been denied.", value=f"**Reason:** {self.reason.value}", inline=False)
        embed_dm.set_footer(text="Contact management for further details.")

        try:
            await self.requester.send(embed=embed_dm)
        except:
            pass

        await interaction.response.send_message("✅ LOA request denied.", ephemeral=True)

# Setup function for bot to load the cog
async def setup(bot):
    await bot.add_cog(LOARequest(bot))