# save as coin_bot.py
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import discord
from discord.ext import tasks, commands

ROLE_ID = "1388308630415343656"

# Use an env var for token; never paste token in logs
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1388304295551565926  # replace with your channel id (int)
TZ = ZoneInfo("America/Denver")   # user's timezone
START_TIME = datetime(2025, 8, 9, 22, 0, tzinfo=TZ)
CYCLE_HOURS = 20

# --- Intents ---
intents = discord.Intents.default()
intents.message_content = True   # <-- required for prefix commands / reading message text
intents.members = True           # optional, only if you need member info

bot = commands.Bot(command_prefix="!", intents=intents)

def seconds_until_next_coin():
    now = datetime.now(TZ)
    elapsed = (now - START_TIME).total_seconds()
    cycle = CYCLE_HOURS * 3600
    remainder = elapsed % cycle
    secs_left = cycle - remainder
    # if exactly at boundary, secs_left == cycle; treat as 0
    if abs(secs_left - cycle) < 1:
        return 0
    return int(secs_left)

@tasks.loop(hours=1)
async def hourly_reminder():
    # fetch_channel is safer than get_channel (cache)
    channel = await bot.fetch_channel(CHANNEL_ID)
    secs_left = seconds_until_next_coin()
    if secs_left == 0:
        # make sure bot role has "Mention @everyone" permission in server/channel
        await channel.send("<@&1388308630415343656> BLACK MARKET IN STOCK!")
    else:
        hrs = secs_left // 3600
        mins = (secs_left % 3600) // 60
        await channel.send(f"⏳ **{hrs} hours {mins} minutes left** until the next black market restock.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    if not hourly_reminder.is_running():
        hourly_reminder.start()
    # If you want slash commands: await bot.tree.sync()

@bot.event
async def on_message(message):
    # If you override on_message, you MUST process commands or they won't run:
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# example quick command
@bot.command()
async def timeleft(ctx):
    secs_left = seconds_until_next_coin()
    hrs = secs_left // 3600
    mins = (secs_left % 3600) // 60
    await ctx.send(f"⏳ **{hrs} hours and {mins} minutes left**")

bot.run(TOKEN)
