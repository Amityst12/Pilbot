import discord
import requests
import json
from discord.ext import commands
import os
from dotenv import load_dotenv
from tft13Dicts import Champions_dict_tft13

# Load the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
BASE_URL = "https://europe.api.riotgames.com"
BOT_PICTURE = "https://media.discordapp.net/attachments/374662463926566914/1323692905713635398/file-Pjkb249pb3APyfoq8ZER2s.png?ex=67757095&is=67741f15&hm=883e522e8150e98b842395e247c20359a583163e7f9ad21b966e52e4bd6aa592&=&format=webp&quality=lossless&width=676&height=676"



# Create an instance of the bot with required intents
intents = discord.Intents.all()  # Use default intents
intents.message_content = True
intents.presences = True 
bot = commands.Bot(command_prefix='TFT ', intents=intents, case_insensitive=True)
bot.remove_command("help")

# Types of TFT mode
tft_game_type = {
    "pairs" : "Double up",
    "RANKED_TFT_DOUBLE_UP" : "Double up",
    "standard" : "Standard",
    "RANKED_TFT" : "Ranked",
    "MATCHED" : "Standard",
    "turbo" : "Hyper Roll",
    "RANKED_TFT_TURBO" : "Hyper Roll",
    "pve" : "PVE"
}




## USE JSON FUNCTIONS FOR INFO SECTION ##

# Reading json
def readJSON(PATH):
    try:
        with open(f"Cache/{PATH}.json", 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File not found - Cache/{PATH}.json")  # Debug: Handle missing file
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file Cache/{PATH}.json: {e}")  # Debug: Handle bad JSON
        return None

# Write to json
def writeJSON(PATH, data):
    try:
        with open(f"Cache/{PATH}", 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error writing to file Cache/{PATH}: {e}")  # Debug: Catch and report any exceptions

# Writing game analysis [ITEMS ON UNITS WINRATE]
def itemsForUnitsJSON(FileName, new_items, gameid, player_puuid, placement):
    file_path = f"Cache/Units/{FileName}.json"

    # Check if file exists and load its data; otherwise, initialize a new dictionary
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # If the file exists but is empty or invalid, initialize an empty dictionary
    else:
        data = {}
        
    if gameid not in data:
        data[gameid] = {}

    # Make new palyer_puuid dict
    top4 = False
    top1 = False
    if placement <= 4 : top4= True 
    if placement == 1 : top1 = True
    
    
    if player_puuid not in data[gameid]:
        data[gameid][player_puuid] = {
            "top4" : top4,
            "top1" : top1,
            "items": new_items
        }
    else:
        # Convert the string to a list if it's not already a list
        if isinstance(data[gameid][player_puuid]["items"], str):
            data[gameid][player_puuid]["items"] = data[gameid][player_puuid]["items"].split(", ")
        
        if new_items not in data[gameid][player_puuid]["items"]:
            data[gameid][player_puuid]["items"].extend(new_items)

    # Save the updated data back to the file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Writing game analysis [UNITS ON PLAYERS WINRATE]  ---- FileName is PUUID
def unitsOnPlayersJSON(FileName, new_data, gameid, placement): 
    file_path = f"Cache/Summoners/{FileName}.json"
    
    # Check if file exists and load its data; otherwise, initialize a new dictionary
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # If the file exists but is empty or invalid, initialize an empty dictionary
    else:
        data = {}
    if gameid not in data:
        data[gameid] = {}
    # Make new palyer_puuid dict
    top4 = False
    top1 = False
    if placement <= 4 : top4= True 
    if placement == 1 : top1 = True
    if gameid not in data[gameid]:
        data[gameid] = {
            "top4" : top4,
            "top1" : top1,
            "units": new_data, 
        }
    else:
        # Update the list of items if needed or skip if already processed
        if new_data not in data[gameid]:
            data[gameid].extend(new_data)

    # Save the updated data back to the file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    
# Game analyzed +1
def updateGamesAnalyzed(game_id):
    data = readJSON("General/gamesAnalyzed")
    ids = data["ids"]
    amount = data["Games"]
    
    if game_id not in data["ids"]:
        amount += 1
        ids.append(game_id)
        new_data = {"Games" : amount,
                     "ids" : ids}
        writeJSON("General/gamesAnalyzed.json", new_data)
        return True
    
    return False

# Analyze game items for units
def AnalyzeGameUnits(GameData):
    for player in GameData["info"]["participants"]:
        units_list = ""
        units_list = ", ".join(unit["character_id"] for unit in player["units"])
        
        for unit in player["units"]:
            items = ""
            items = ", ".join(unit["itemNames"])  # Join items dynamically
            itemsForUnitsJSON(unit["character_id"], items, GameData["metadata"]["match_id"], player["puuid"], player["placement"])
        
        unitsOnPlayersJSON(player["puuid"], units_list, GameData["metadata"]["match_id"], player["placement"])




## USE API FUNCTIONS FOR INFO SECTION ##

# Returns player's PUUID
def getPUUID(Summoner_name, Player_tag = "eune"):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{Summoner_name}/{Player_tag}"
    url = url +'?api_key=' + str(RIOT_API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        summoner_data = response.json()
        Encrypted_PUUID = summoner_data.get('puuid', 'Unknown')
        return Encrypted_PUUID
    print(f"Coudlnt reach {Summoner_name}'s PUUID")
    return False

# Returns [ID's] of matches
def getTFTmatches(PUUID, count = 1):
    url = f"{BASE_URL}/tft/match/v1/matches/by-puuid/{PUUID}/ids?start=0&count={count}&api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        Matches = response.json()
        return Matches
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
    print(f"Could not gain data from match")
    return False

# Returns player name using PUUID        
def getSummonerNameFromPUUID(PUUID):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-puuid/{PUUID}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        Player_data = response.json()
        return Player_data["gameName"]
    print(f"Could not gain data from PUUID")
    return False
    
# Returns summonerInfo using PUUID
def getSummonerInfoFromPUUID(PUUID):
    url = f"https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{PUUID}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        Summoner_data = response.json()
        return Summoner_data
    else:
        print(f"Could not reach getSummonerIdFromPUUID")
        return False

# Returns all TFT info for player
def getTFTinfoFromSummonerId(summonerId):
    url = f"https://eun1.api.riotgames.com/tft/league/v1/entries/by-summoner/{summonerId}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    if response.status_code ==200:
        Player_data = response.json()
        return Player_data
    print(f"Could not reach getTFTinfoFromSummonerId")
    return False

# Returns active game using PUUID
def getSpectatorTFTFromPUUID(PUUID):
    url = f"https://eun1.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/{PUUID}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    print(url)
    if response.status_code == 200:
        Match_data = response.json()
        return Match_data
    print("Could not reach getSpectatorTFTFromPUUID")
    return False

# Returns accurate rank for player (Masters+)
def getAccurateRank(summonerID, queue):
    #RANKED_TFT_DOUBLE_UP , RANKED_TFT
    position = 1
    options = ["challenger" , "grandmaster", "master"]
    for i in range(0,3):
        url = f"https://eun1.api.riotgames.com/tft/league/v1/{options[i]}?queue={queue}&api_key={RIOT_API_KEY}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Could not reach {options[i]} ladder")
            return ""
        Ladder = response.json()
        for player in Ladder["entries"]:
            if player["summonerId"] == summonerID: return f" **#{position}**🎖"
            position+= 1
    print("Could not find player in ladder")
    return ""
    
    


## APP EVENTS SECTION ##

# Logged
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Error accured
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing argument. Please provide the required information.")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("There was an error processing your command.")
        print(f"Command error: {error}")
    else:
        await ctx.send("An unexpected error occurred, maybe an unrecognized command")

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


     
     
## APP COMMANDS SECTION ##     
     
# Menu command for APP
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title=f"Hi, I am Pilbot",
        description="•Get started with Pilbot by using the commands below.\n• Currently featuring EU only.",
        color=discord.Color.pink() 
    )
    embed.set_author(name= "Pilbot", icon_url=BOT_PICTURE, url="" )
    embed.set_thumbnail(url=BOT_PICTURE)
    embed.add_field(
        name="⚙️**My prefix is 'TFT'**",
        value=f"• Before every command you type TFT to execute it\n• example: TFT (command name) etc... ",
        inline=False
    )
    embed.add_field(
        name="📸**TFT profile (playerID) (playerTAG)**",
        value="• Check a tft profile! \n• Ranked? Double up? we got eveything.",
        inline=False
    )    
    embed.add_field(
        name="🏆**TFT history (playerID) (playerTAG) (1-10)**",
        value="• Check for player's last few matches.",
        inline=False
    )
    embed.add_field(
        name="**🕹️TFT ingame (playerID) (playerTAG)**",
        value="• Check for player's ongoing game.",
        inline =False
    )
    embed.add_field(
        name="**Disclamer**",
        value="• Don't use spacebar on playerID,\n• Don't use '#' on playerTAG",
        inline=False
    )
    embed.set_footer(text="App created by: Amityst12, using Riot's API")
    await ctx.send(embed=embed)


# Info command about player
@bot.command()
async def profile(ctx, summoner_name: str, summoner_tag: str = "eune"):
    PUUID = getPUUID(summoner_name, summoner_tag)
    summonerDATA = getSummonerInfoFromPUUID(PUUID)
    summonerID = summonerDATA["id"]
    summonerName = getSummonerNameFromPUUID(PUUID)
    profile_icon = f"https://ddragon.leagueoflegends.com/cdn/14.24.1/img/profileicon/{summonerDATA["profileIconId"]}.png"
    if not PUUID or not summonerID:
        await ctx.send("Sorry, I couldn't find that summoner.")
        return

    player_info = getTFTinfoFromSummonerId(summonerID)
    if not player_info:
        await ctx.send("This player did not play TFT... YET!")
        return
    # Create an Embed
    embed = discord.Embed(
        title=f"{summonerName}'s profile:",
        color=discord.Color.blue(), 
    ).set_author(name= "Pilbot", icon_url=BOT_PICTURE, url="" )
    
    found_game = False  # To track if we found any relevant game data
    for x in player_info:
        if x["queueType"] == "RANKED_TFT_DOUBLE_UP":                                  # Double up
            if (x["losses"] + x["wins"]) != 0:
                doubleupWR = x["wins"] / (x["wins"] + x["losses"]) * 100
                doubleupWR = round(doubleupWR, 2)
                value=f"{x['tier']} {x['rank']} - {x['leaguePoints']}LP {getAccurateRank(summonerID,"RANKED_TFT_DOUBLE_UP")} \n Top 2 W/R: {doubleupWR}%"
                if x["hotStreak"] == True:
                    value +=f"\n **{summonerName} is on a winstreak!**🔥"
                if x["freshBlood"] == True:
                    value +=f"\n **{summonerName} just ranked up!**"
                if x["inactive"] == True:
                    value +=f"\n **{summonerName} is inactive😕.**"
                embed.add_field(
                    name="•Double Up",
                    value=value,
                    inline=False
                )
                found_game = True

        if x["queueType"] == "RANKED_TFT":                                             # Ranked
            if (x["losses"] + x["wins"]) != 0:
                rankedWR = x["wins"] / (x["wins"] + x["losses"]) * 100
                rankedWR = round(rankedWR, 2)
                value = f"{x['tier']} {x['rank']} - {x['leaguePoints']}LP {getAccurateRank(summonerID,"RANKED_TFT")}\n Top 4 W/R: {rankedWR}%"
                if x["hotStreak"] == True:
                    value +=f"\n **{summonerName} is on a winstreak!**🔥"
                if x["freshBlood"] == True:
                    value +=f"\n **{summonerName} just ranked up!**"
                if x["inactive"] == True:
                    value +=f"\n **{summonerName} is inactive😕.**"
                embed.add_field(
                    name="•Ranked",
                    value=value,
                    inline=False
                )
                found_game = True

        if x["queueType"] == "RANKED_TFT_TURBO":                                        # Hyperoll
            if (x["losses"] + x["wins"]) != 0:
                hrWR = x["wins"] / (x["wins"] + x["losses"]) * 100
                hrWR = round(hrWR, 2)
                value =f"{x['ratedTier']}, {x['ratedRating']} Rating\n Top 4 W/R: {hrWR}%"
                embed.add_field(
                    name="•HyperRoll",
                    value= value,
                    inline=False
                )
                found_game = True   
    if not found_game:
        embed.description = f"Sorry, {summoner_name} did not play any game recently."
    else:
        embed.set_thumbnail(url=profile_icon)
        embed.set_footer(text="Data retrieved from Riot Games API")
        

    await ctx.send(embed=embed)


# Current match
@bot.command()
async def ingame(ctx, summoner_name: str, summoner_tag:str ="eune"):
    PUUID = getPUUID(summoner_name, summoner_tag)
    if not PUUID:
        await ctx.send("Player not found")
        return
    
    Match_info = getSpectatorTFTFromPUUID(PUUID)
    if not Match_info:
        await ctx.send("Player is not in game")
        return
    
    summonerDATA = getSummonerInfoFromPUUID(PUUID)
    if not summonerDATA:
        await ctx.send("Could not retrieve summonerDATA")
        return
    
    profile_icon = f"https://ddragon.leagueoflegends.com/cdn/14.24.1/img/profileicon/{summonerDATA["profileIconId"]}.png"
    gametime = f"{int(Match_info["gameLength"]/60)}:{Match_info["gameLength"]%60}"
    
    Players = f""
    for player in Match_info["participants"]:
        if player["puuid"] == PUUID:
            player_name = player["riotId"]
            player_name = player_name.split('#')[0]
            Players += f"{player_name} 👈 You\n"
        else:
            name = player["riotId"]
            name = name.split('#')[0]
            Players += f"{name}\n"
            
    # Create the Embed match        
    embed = discord.Embed(
        title=f"{player_name}'s live game:",
        description=f"Game time: {gametime}",
        color=discord.Color.green()
    ).set_thumbnail(url = profile_icon)
        
    embed.add_field(name= "Players:", value=Players, inline=False)
    embed.set_author(name= "Pilbot", icon_url=BOT_PICTURE, url="" )
    embed.set_footer(text=f"Match ID: {Match_info["gameId"]}")
    await ctx.send(embed=embed)
    
        
# Returns match history for {games} matches
@bot.command()
async def history(ctx, summoner_name: str, summoner_tag: str = "eune", games: int = 1):
    PUUID = getPUUID(summoner_name, summoner_tag)
    if PUUID == False or games > 10:
        print("getPUUID went wrong.")
        await ctx.send("Sorry, something went wrong.")
        return

    Match = getTFTmatches(PUUID, games)
    if Match == False:
        print("getTFTmatches went wrong.")
        await ctx.send("Sorry, something went wrong.")
        return

    if len(Match) == 0:
        await ctx.send(f"No matches found for {summoner_name}")
        print(f"No matches found for {summoner_name}")
        return

    gamecounter = 1
    for matches in Match:
        Match_info = getTFTmatchInfo(matches)

        # Create the Embed for each match
        embed = discord.Embed(
            title=f"Game {gamecounter} - {tft_game_type[Match_info['info']['tft_game_type']]}",
            description="vvvvvvvvvvvvvvvvvvvv",
            color=discord.Color.green()
        )

        participants = Match_info["info"]["participants"]
        sorted_players = sorted(participants, key=lambda x: x["placement"])
        Suffixes = {1: "st", 2: "nd", 3: "rd", 4: "th", 5: "th", 6: "th", 7: "th", 8: "th"}
        duSuffixes = {1: "1st", 2: "1st", 3: "2nd", 4: "2nd", 5: "3rd", 6: "3rd", 7: "4th", 8: "4th"}
        
        # Add participants to the embed
        i = 0
        addon = ""
        while i < len(sorted_players):
            player = sorted_players[i]
            if tft_game_type[Match_info["info"]["tft_game_type"]] == "Double up" and i + 1 < len(sorted_players):
                next_player = sorted_players[i + 1]
                placement = duSuffixes[player["placement"]]
                if player["puuid"] == PUUID  or next_player["puuid"] == PUUID :  addon = "  👈 You"
                embed.add_field(
                    name=f"{placement}",
                    value=f"{player['riotIdGameName']} + {next_player['riotIdGameName']}{addon}",
                    inline=False
                )
                addon = ""
                i += 2  # Skip to the next pair
            else:
                if player["puuid"] == PUUID : addon = "  👈 You"
                placement = f"{player['placement']}{Suffixes[player['placement']]}"
                embed.add_field(
                    name=f"{placement}",
                    value=f"{player['riotIdGameName']}{addon}",
                    inline=False
                )
                addon = ""
                i += 1
        embed.set_author(name= "Pilbot", icon_url=BOT_PICTURE, url="" )
        embed.set_footer(text=f"Match ID: {matches}")
        gamecounter += 1


        await ctx.send(embed=embed)
        if tft_game_type[Match_info["info"]["tft_game_type"]] != "Hyper Roll" and tft_game_type[Match_info["info"]["tft_game_type"]] != "PVE":
            if updateGamesAnalyzed(matches):
                AnalyzeGameUnits(Match_info)
    
    print(f"Sent info for {summoner_name}'s last {games} games.")
        
        



# Run.
bot.run(TOKEN)
