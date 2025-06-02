##############################################################
# Imports
##############################################################
import discord
import os 
import json 
import logging
from discord.ext import commands
from discord.ui import Button, View
from discord.ext.commands import CommandNotFound, MissingPermissions
from dotenv import load_dotenv

##############################################################
# Configuration & Global Variables
##############################################################
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
load_dotenv()  
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    raise ValueError("No bot token found in .env file. Please add BOT_TOKEN=your_token_here to .env")

USER_POSSESIONS = "user_possessions"

PACK_PRICES = {
    "regular": 50,
    "rare": 200,
    "lucky": 1500,
    "master": 5500,
    "legend": 15500
}

PACK_SGC_PRICES = {
    "ultimate": 10,
    "sand": 25,
    "special": 50
}

CARD_RARITIES = {
    "common": (50, 70),     # (min_rating, max_rating)
    "uncommon": (65, 80),
    "rare": (75, 85),
    "epic": (80, 90),
    "legendary": (85, 95),
    "mythic": (90, 100),
    "dev": (95, 105)
}

##############################################################
# Data Management Functions
##############################################################
def load_data():
    if not os.path.exists(USER_POSSESIONS):
        with open(USER_POSSESIONS, "w") as f:
            json.dump({}, f)
    with open(USER_POSSESIONS, "r") as f:
        return json.load(f)

def save_data(data):
    with open(USER_POSSESIONS, "w") as f:
        json.dump(data, f, indent=4)

def check_for_user(user_id, starting_money: int=500):
    user_id = str(user_id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            "credits": starting_money,
            "sgc": 0,                  # Sand Grain Credits
            "team": {
                "assault": None,
                "sharpshooter": None,
                "medic": None,
                "shield_trooper": None,
                "jet_trooper": None,
                "engineer": None,
                "pilot": None,
                "barc": None
            },
            "cards": [],
            "battle_cooldown": None,   # for battle system
            "battles_remaining": 5     # daily battle counter
        }
        save_data(data)
        return True
    return False

##############################################################
# Bot Setup
##############################################################
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    if bot.user:
        print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
        print("------")
    else:
        print("Bot logged in but user is None!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("That command doesn't exist! Use `!help` to see all available commands.")
    elif isinstance(error, MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

##############################################################
# Bot Commands
##############################################################
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name='enter')
async def enter_command(ctx):
    data = load_data()
    if str(ctx.author.id) in data:
        await ctx.send("You've already joined! Use !balance to check your credits.")
        return

    embed = discord.Embed(
        title="Welcome",
        description="So you've finally decided to join the leagues",
        color=discord.Color.yellow(),
    )
    embed.add_field(name="starter loot", value="💵 500 big bucks 💵", inline=False)
    
    button_accept = discord.ui.Button(label="Where do I sign?", style=discord.ButtonStyle.green)
    async def accept(interaction: discord.Interaction):
        if not interaction.user:
            await interaction.response.send_message("An error occurred. Please try again.", ephemeral=True)
            return
            
        user_id = str(interaction.user.id)
        if check_for_user(user_id, starting_money=500):
            await interaction.response.send_message("Welcome! The money has been deposited into your account.", ephemeral=True)
        else:
            await interaction.response.send_message("You've already joined!", ephemeral=True)
            
    button_accept.callback = accept

    button_refuse = discord.ui.Button(label="Mabye later", style=discord.ButtonStyle.red)
    async def refuse(interaction):
        await interaction.response.send_message("Call me if you change your mind!", ephemeral=True)
    button_refuse.callback = refuse

    view = discord.ui.View()
    view.add_item(button_accept)
    view.add_item(button_refuse)
    
    await ctx.send(embed=embed,view=view)

@bot.command(name='balance', aliases=['bal'])
async def balance(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    
    if user_id not in data:
        await ctx.send("You haven't joined yet! Use !enter to start.")
        return
        
    user_data = data[user_id]
    embed = discord.Embed(
        title=f"{ctx.author.name}'s Balance",
        color=discord.Color.green()
    )
    embed.add_field(name="235th Credits", value=f"💵 {user_data['credits']}", inline=True)
    embed.add_field(name="Sand Grain Credits", value=f"🌟 {user_data['sgc']}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='packs')
async def show_packs(ctx):
    embed = discord.Embed(
        title="Available Card Packs",
        description="Here are all available packs for purchase:",
        color=discord.Color.blue()
    )
    
    # Regular packs
    regular_packs = "\n".join([f"{name.title()} Pack: {price} Credits" 
                              for name, price in PACK_PRICES.items()])
    embed.add_field(name="Credit Packs", value=regular_packs, inline=False)
    
    # SGC packs
    sgc_packs = "\n".join([f"{name.title()} Pack: {price} SGC" 
                          for name, price in PACK_SGC_PRICES.items()])
    embed.add_field(name="SGC Packs", value=sgc_packs, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='commands', aliases=['cmds'])
async def commands_list(ctx):
    embed = discord.Embed(
        title="TCG Bot Help",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )
    
    commands_list = {
        "Getting Started": {
            "!enter": "Join the game and receive your starting credits",
            "!commands (!cmds)": "Show this help message",
        },
        "Economy": {
            "!balance (!bal)": "Check your credits and SGC balance",
            "!packs": "View available card packs",
        }
    }
    
    for category, cmds in commands_list.items():
        command_text = "\n".join([f"`{cmd}`: {desc}" for cmd, desc in cmds.items()])
        embed.add_field(name=category, value=command_text, inline=False)
    
    embed.set_footer(text="More features coming soon!")
    await ctx.send(embed=embed)

##############################################################
# Bot Startup
##############################################################
bot.run(bot_token)
