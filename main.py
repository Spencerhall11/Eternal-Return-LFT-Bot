import discord
import os 
from discord.ext import commands
from dotenv import load_dotenv

#load ENV to get discord token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class LumiaRumbleBot(commands.Bot):
    def __init__(self):
        #set up the intent gates
        intents = discord.Intents.default()
        #allow reading member data
        intents.members = True 
        #allow reading message
        intents.message_content = True

        #intialize the class
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        #this runs before the bot starts. loads the cogs and commands
        #check if recruitment cog is there
        try:
            await self.load_extension('cogs.recruitment')
            print("Loaded: Recruitment")
        except Exception as e:
            print(f"Could not load Recruitment: {e}")

        #register slash commands with discord
        await self.tree.sync()
        print("Slash commands synced to Discord.")

    async def on_ready(self):
        #runs when bot is on and connected
        print(f'--- Logged in as {self.user} ---')
        print(f'ID: {self.user.id}')   

#start the bot after creating instance
if __name__ == "__main__":
    bot = LumiaRumbleBot()
    bot.run(TOKEN)