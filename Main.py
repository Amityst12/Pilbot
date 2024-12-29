import discord
import requests
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
BASE_URL = "https://europe.api.riotgames.com"
print("DISCORD_BOT_TOKEN:", TOKEN)
print("RIOT_API_KEY:", RIOT_API_KEY)

# Create an instance of the bot with required intents
intents = discord.Intents.all()  # Use default intents
intents.message_content = True
intents.presences = True 
bot = commands.Bot(command_prefix='TFT ', intents=intents)

# Types of TFT mode
tft_game_type = {
    "pairs" : "Double up",
    "standard" : "Standard",
    "turbo" : "Hyper Roll",
    "pve" : "PVE"
}

# Returns player's PUUID
def getPUUID(Summoner_name, Player_tag = "eune"):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{Summoner_name}/{Player_tag}"
    url = url +'?api_key=' + str(RIOT_API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        summoner_data = response.json()
        Encrypted_PUUID = summoner_data.get('puuid', 'Unknown')
        return Encrypted_PUUID
    else:
        print(f"Coudlnt reach {Summoner_name}'s PUUID")
        return False

# Returns [ID's] of matches 
def getTFTmatches(PUUID, count = 1):
    url = f"{BASE_URL}/tft/match/v1/matches/by-puuid/{PUUID}/ids?start=0&count={count}&api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        Matches = response.json()
        return Matches
    else:
        print(f"Couldnt satisfy getTFTmatches")
        return False

# Returns info about match 
def getTFTmatchInfo(matchId):
    url = f"{BASE_URL}/tft/match/v1/matches/{matchId}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    print(url)
    if response.status_code == 200:
        Match_data = response.json()
        return Match_data
    else:
        print(f"Could not gain data from match")
        return False

# Returns player name using PUUID        
def getSummonerNameFromPUUID(PUUID):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-puuid/{PUUID}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        Player_data = response.json()
        return Player_data["gameName"]
    else:
        print(f"Could not gain data from PUUID")
        return False


# @bot.event - Waiting for an event to happen then responds
# Logged
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Sets up recievent messages and responds to ping
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.lower() == "ping":
        await message.channel.send("pong")
        print(f"Ponged")
        return
    
    # This is necessary to allow commands to work
    await bot.process_commands(message)

     
# @bot.command() - Responding to prefix ( 0 ) command
# Regualr Hello command
@bot.command()
async def hello(ctx):
    user_name = ctx.author.display_name
    await ctx.send(f"Hello, {user_name}")
    try: print(f"Greeted {user_name}")
    except ValueError as e: print(f"Greeted {ctx.author.name}")

# Summoner command
@bot.command()
async def summoner(ctx, summoner_name: str , summoner_tag: str = "eune"):
    PUUID = getPUUID(summoner_name,summoner_tag)
    if PUUID == False:
        await ctx.send("Sorry, I couldn't find that summoner.")
    else:
        await ctx.send(f"Summoner {summoner_name}, info: {PUUID}.")

# Returns match history for {games} matches
@bot.command()
async def history(ctx, summoner_name:str , summoner_tag:str ="eune" , games = 1):
    PUUID = getPUUID(summoner_name, summoner_tag) # Getting PUUID of desired player
    if PUUID == False:
        print(f"getPUUID went wrong.")
        await ctx.send("Sorry, something went wrong")
        pass
    
    Match = getTFTmatches(PUUID, games)           # Getting desired amount of games
    if Match == False:
        print(f"getTFTmatches went wrong.")
        await ctx.send("Sorry, something went wrong")
        pass
    
    if len(Match) == 0:                           # Checking if there are any games
        await ctx.send(f"No matches found for {summoner_name}")
        print(f"No matches found for {summoner_name}")
        pass
    
    gamecounter = 1
    for matches in Match:
        Match_info = getTFTmatchInfo(matches)
        
        Answer = (
            f"Game {gamecounter}:\n"
            f"------------------------------------------------\n"
            f"Game mode: {tft_game_type[Match_info["info"]["tft_game_type"]]}\n"
            f"Players:\n"
        )
        participants = Match_info["info"]["participants"]                                   # List of participants
        sorted_players = sorted(participants, key=lambda x: x["placement"])                 # Sort first to last
        Suffixes = {1: "st", 2: "nd", 3: "rd", 4:"th",5:"th",6:"th",7:"th",8:"th"}          # Suffix for normal
        duSuffixes ={1: "1st", 2: "1st", 3: "2nd", 4:"2nd",5:"3rd",6:"3rd",7:"4th",8:"4th"} # Suffix for doubleup
        for player in sorted_players:
            if tft_game_type[Match_info["info"]["tft_game_type"]] == "Double up":
                Answer += f"{duSuffixes[player["placement"]]}-  {player["riotIdGameName"]}\n"
            else :
                Answer += f"{player["placement"]}{Suffixes[player["placement"]]}-  {player["riotIdGameName"]}\n"
                
            
        Answer += "------------------------------------------------"
        
        gamecounter += 1    
        await ctx.send(Answer)
            
    print(f"Sent info for {summoner_name}'s last {games} games")
        
        
    


# Run.
bot.run(TOKEN)
