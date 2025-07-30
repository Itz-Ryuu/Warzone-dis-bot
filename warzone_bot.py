import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import random
import os

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Channel ID for auto-posting (replace this)
CHANNEL_ID = 123456789012345678  # Replace with your channel ID

# Loadouts dictionary
warzone_loadouts = {
    "mcw": {
        "name": "MCW",
        "attachments": [
            "Muzzle: Shadowstrike Suppressor",
            "Barrel: 16.5\" MCW Cyclone",
            "Optic: Slate Reflector",
            "Underbarrel: Bruen Heavy Support Grip",
            "Magazine: 60 Round Drum"
        ]
    },
    "ram7": {
        "name": "RAM-7",
        "attachments": [
            "Muzzle: ZEHMN35 Compensator",
            "Barrel: Cronen Headwind Long",
            "Underbarrel: Bruen Heavy Support",
            "Optic: Cronen Mini Pro",
            "Magazine: 60 Round Drum"
        ]
    },
    "katt": {
        "name": "KATT-AMR",
        "attachments": [
            "Muzzle: Sonic Suppressor XL",
            "Barrel: Perdition 24.5\"",
            "Laser: FSS OLE-V Laser",
            "Stock: Tactical Stock Pad",
            "Rear Grip: Phantom Grip"
        ]
    }
}

# Get Warzone news from Call of Duty website
def get_warzone_news():
    url = "https://www.callofduty.com/blog"
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        articles = soup.find_all("a", class_="Card-titleLink", limit=10)
        news_list = []
        for article in articles:
            title = article.text.strip()
            link = "https://www.callofduty.com" + article['href']
            if "warzone" in link.lower():
                news_list.append((title, link))
        return news_list if news_list else []
    except Exception as e:
        return []

# Bot Events
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    post_daily_news.start()

# Bot Commands

@bot.command()
async def warzone(ctx):
    news = get_warzone_news()
    if not news:
        await ctx.send("❌ No recent Warzone news found.")
        return
    embed = discord.Embed(title="📢 Warzone News", color=0x00A2FF)
    for title, link in news:
        embed.add_field(name=title, value=f"[Read more]({link})", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def loadout(ctx, weapon: str):
    weapon = weapon.lower()
    if weapon in warzone_loadouts:
        data = warzone_loadouts[weapon]
        embed = discord.Embed(title=f"🎯 {data['name']} Loadout", color=0xFFA500)
        for i, att in enumerate(data['attachments'], start=1):
            embed.add_field(name=f"Attachment {i}", value=att, inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Loadout not found. Use `!loadouts` to see available weapons.")

@bot.command()
async def loadouts(ctx):
    weapons = ', '.join(warzone_loadouts.keys())
    embed = discord.Embed(title="🔫 Available Warzone Loadouts", description=weapons.upper(), color=0x1ABC9C)
    await ctx.send(embed=embed)

@bot.command()
async def randomloadout(ctx):
    weapon = random.choice(list(warzone_loadouts.keys()))
    data = warzone_loadouts[weapon]
    embed = discord.Embed(title=f"🎲 Random Loadout: {data['name']}", color=0x9B59B6)
    for i, att in enumerate(data['attachments'], start=1):
        embed.add_field(name=f"Attachment {i}", value=att, inline=False)
    await ctx.send(embed=embed)

# Auto-post daily news
@tasks.loop(hours=24)
async def post_daily_news():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        news = get_warzone_news()
        if news:
            embed = discord.Embed(title="🗞️ Daily Warzone News", color=0x00A2FF)
            for title, link in news:
                embed.add_field(name=title, value=f"[Read more]({link})", inline=False)
            await channel.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))