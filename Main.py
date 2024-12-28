import discord
import requests
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
BASE_URL = "https://api.riotgames.com/tft"
print("DISCORD_BOT_TOKEN:", TOKEN)
print("RIOT_API_KEY:", RIOT_API_KEY)

# Create an instance of the bot with required intents
intents = discord.Intents.all()  # Use default intents
intents.message_content = True
intents.presences = True 
bot = commands.Bot(command_prefix='0', intents=intents)


# @bot.event - Waiting for an event to happen then responds
# Logged
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Sets up recievent messages and responds to ping
@bot.event
async def on_message(message):
    if message.content == "ping":
        await message.channel.send("pong")
        print(f"Ponged")
    # This is necessary to allow commands to work
    await bot.process_commands(message)
    
@bot.command()
async def summoner(ctx, summoner_name: str , summoner_tag: str):
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}"
    url = url +'?api_key=' + str(RIOT_API_KEY)
    response = requests.get(url)
    print(f"Gathered info from {url}")
    
    if response.status_code == 200:
        summoner_data = response.json()
        # You can process the data to get the player’s rank, level, etc.
        summoner_info = summoner_data.get('puuid', 'Unknown')
        await ctx.send(f"Summoner {summoner_name}, info: {summoner_info}.")
    else:
        await ctx.send("Sorry, I couldn't find that summoner.")

     
# @bot.command() - Responding to prefix ( 0 ) command
# Regualr Hello command
@bot.command()
async def hello(ctx):
    user_name = ctx.author.display_name
    await ctx.send(f"Hello, {user_name}")
    try: print(f"Greeted {user_name}")
    except ValueError as e: print(f"Greeted {ctx.author.name}")

# Regualr sum command
@bot.command()
async def add(ctx, num1: int, num2: int):
    result = num1 + num2
    if result == 5: await ctx.send(f"ELBIT")
    else: await ctx.send(f"The result is {result}")





# Run.
bot.run(TOKEN)
