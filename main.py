##############################################################
###################### imports ###############################
##############################################################
import discord
import os 
import json 
import logging

from discord.ext import commands
from discord.ui import Button, View 
from dotenv import load_dotenv

#==============================================================
#global variables and config
#==============================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name):s %(message)s')


load_dotenv()  
bot_token = os.getenv("BOT_TOKEN")




#==============================================================
# genral setup
# =============================================================

USER_POSSESIONS = "user_possessions"

def load_data():
    if not os.path.exists(USER_POSSESIONS):
        with open(USER_POSSESIONS, "w") as f:
            json.dump({}, f)
    with open(USER_POSSESIONS, "r") as f:
        return json.load(f)

def save_data(data):
    with open(USER_POSSESIONS, "w") as f:
        json.dump(data, f, indent=4)

#=============================================================
#bot setup
#==============================================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


#==========================================================
#functions
#==========================================================
def check_for_user(user_id,starting_money: int=500):
    user_id = str(user_id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            "money": starting_money,
            "upgrades": [],
            "cards": []
        }
        save_data(data)
        return True
    return False



#===========================================================
#bot commands
#==========================================================
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name='enter')
async def enter_command(ctx):
    embed = discord.Embed(
        title = "Welcome",
        description = "So you've finally decided to join the leages",
        color=discord.Color.yellow(),
    )
    embed.add_field(name="starter loot",value="💵 500 big bucks 💵",inline=False)
    button_accept = discord.ui.Button(label="Where do I sign?", style=discord.ButtonStyle.green)
    async def accept(interaction):
        await interaction.response.send_message("The money will be deposited into your account shortly", ephemeral=True)
        check_for_user(interaction.user.id, starting_money = 500)
    button_accept.callback = accept

    button_refuse = discord.ui.Button(label="Mabye later", style=discord.ButtonStyle.red)
    async def refuse(interaction):
        await interaction.response.send_message("Call me if you change your mind!", ephemeral=True)
    button_refuse.callback = refuse

    view = discord.ui.View()
    view.add_item(button_accept)
    view.add_item(button_refuse)
    


    await ctx.send(embed=embed,view=view)


bot.run(bot_token)









# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('bot_token')
