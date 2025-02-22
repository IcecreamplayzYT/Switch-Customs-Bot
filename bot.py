import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio  # Required for async functions

# 🔹 Bot Intents (Fixes Missing Privileged Intent Warning)
intents = discord.Intents.default()
intents.members = True  # Required for detecting new members
intents.message_content = True  # Fixes warning

# 🔹 Initialize Bot
bot = commands.Bot(command_prefix="s?", intents=intents)

# 🔹 Server Configuration
GUILD_ID = 1342198087933755555  # Server ID
AUTO_ROLE_ID = 1342201876405555332  # Auto-role ID
WELCOME_CHANNEL_ID = 1342198088722546780  # Welcome channel ID
WELCOME_EMOJI_ID = 1342248128270569522  # Custom emoji ID

# 🔹 Load Commands Function
async def load_commands():
    """Loads all command cogs from the commands folder."""
    for filename in os.listdir("commands"):
        if filename.endswith(".py"):
            try:
                module = f"commands.{filename[:-3]}"
                if module in bot.extensions:  # Unload if already loaded
                    await bot.unload_extension(module)
                await bot.load_extension(module)
                print(f"✅ Loaded: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

# 🔹 Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    # Force unload QualityControl cog if it's still loaded
    if "QualityControl" in bot.cogs:
        try:
            bot.remove_cog("QualityControl")
            await bot.unload_extension("commands.qc")
            print("⚠️ Force Unloaded 'QualityControl' Cog")
        except Exception as e:
            print(f"❌ Failed to unload 'QualityControl': {e}")

    await load_commands()  # Reload all commands
    print(f"✅ Final Loaded Cogs: {bot.cogs.keys()}")

    # Sync slash commands
    try:
        synced = await bot.tree.sync()  # Syncs globally instead of just in one server
        print(f"🔗 Synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# 🔹 Auto-Role & Welcome Message
@bot.event
async def on_member_join(member):
    guild = member.guild

    # Assign Auto-Role
    try:
        role = guild.get_role(AUTO_ROLE_ID)
        if role:
            await member.add_roles(role)
    except Exception as e:
        print(f"❌ Failed to assign auto-role: {e}")

    # Fetch custom emoji correctly
    emoji = discord.utils.get(bot.emojis, id=WELCOME_EMOJI_ID)

    # If the emoji is not found, fallback to an empty string
    emoji_text = f"{emoji}" if emoji else ""

    # Send Welcome Message
    try:
        welcome_channel = await bot.fetch_channel(WELCOME_CHANNEL_ID)  # Ensures the correct channel is fetched
        if welcome_channel:
            member_count = guild.member_count
            await welcome_channel.send(f"{emoji_text} Welcome {member.mention} to Switch Customs. You are member {member_count}")
    except Exception as e:
        print(f"❌ Failed to send welcome message: {e}")

# 🔹 Run Bot
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") 