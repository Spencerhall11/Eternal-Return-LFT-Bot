import discord
from discord.ext import commands
from discord import app_commands
from sheets_handler import db


#stores the data
class ProfileState:
    def __init__(self):
        self.data = {
            "name": "N/A", "role": "N/A", "o_roles": "N/A",
            "char": "N/A", "o_chars": "N/A", "link": "N/A"
        }

#modals
class IdentityModal(discord.ui.Modal, title="Step 1: Identity"):
    name = discord.ui.TextInput(label="Account Name", placeholder="PlayerName")
    link = discord.ui.TextInput(label="Dak.gg Link", placeholder="https://dak.gg/...")

    def __init__(self, state):
        super().__init__()
        self.state = state

    async def on_submit(self, interaction: discord.Interaction):
        self.state.data["name"] = self.name.value
        self.state.data["link"] = self.link.value
        await interaction.response.send_message("Identity saved!", ephemeral=True)

class RoleModal(discord.ui.Modal, title="Step 2: Roles"):
    main = discord.ui.TextInput(label="Main Role")
    other = discord.ui.TextInput(label="Other Roles (split by commas)", required=False)
    
    def __init__(self, state):
        super().__init__()
        self.state = state

    async def on_submit(self, interaction: discord.Interaction):
        self.state.data["role"] = self.main.value
        self.state.data["o_roles"] = self.other.value or "None"
        await interaction.response.send_message("Roles saved!", ephemeral=True)

class CharModal(discord.ui.Modal, title="Step 3: Characters"):
    main = discord.ui.TextInput(label="Main Character")
    other = discord.ui.TextInput(label="Other Characters (split by commas)", required=False)
    
    def __init__(self, state):
        super().__init__()
        self.state = state

    async def on_submit(self, interaction: discord.Interaction):
        self.state.data["char"] = self.main.value
        self.state.data["o_chars"] = self.other.value or "None"
        await interaction.response.send_message("Characters saved!", ephemeral=True)

# DASHBOARD VIEW
class RecruitmentView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.state = ProfileState()

    @discord.ui.button(label="1. Identity", style=discord.ButtonStyle.secondary)
    async def identity(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IdentityModal(self.state))

    @discord.ui.button(label="2. Roles", style=discord.ButtonStyle.secondary)
    async def roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RoleModal(self.state))

    @discord.ui.button(label="3. Characters", style=discord.ButtonStyle.secondary)
    async def chars(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CharModal(self.state))

    @discord.ui.button(label="SAVE TO SHEET", style=discord.ButtonStyle.success)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        row = [
            str(self.user_id),
            self.state.data["name"],
            self.state.data["role"],
            self.state.data["o_roles"],
            self.state.data["char"],
            self.state.data["o_chars"],
            self.state.data["link"]
        ]
        status = db.sync_player(row)
        await interaction.followup.send(f"Full profile {status}!")

    @discord.ui.button(label="DELETE LFT RECORD", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        success = db.delete_player(self.user_id)
        
        if success:
            await interaction.followup.send("Your profile has been removed from the LFT list.", ephemeral=True)
        else:
            await interaction.followup.send("I couldn't find a listing for you to delete.", ephemeral=True)

#THE COG
class Recruitment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lft", description="Open your LFT Dashboard in DMs")
    async def lft(self, interaction: discord.Interaction):
        try:
            view = RecruitmentView(interaction.user.id)
            await interaction.user.send("Select a category to update your profile or delete your record:", view=view)
            await interaction.response.send_message("Dashboard sent to DMs!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Enable DMs first!", ephemeral=True)

 @app_commands.command(name="lfp", description="Search for players by role or character")
    @app_commands.describe(query="The role or character you are looking for")
    async def lfp(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(ephemeral=True)
        matches = db.search_players(query)

        if not matches:
            return await interaction.followup.send(f"No players found matching '{query}'.", ephemeral=True)

        response_text = f"**Players matching '{query}':**\n"
        
        for p in matches:
            d_id = p.get('Discord ID') or p.get('DiscordID')
            mention = f"<@{d_id}>" if d_id else "Unknown Player"
            
            name = p.get('Account Name') or p.get('AccountName') or "N/A"
            
            response_text += f"• {mention} ({name})\n"

        await interaction.followup.send(response_text, ephemeral=True)

    @app_commands.command(name="lumia_help", description="How to use the LFT/LFP system")
    async def lumia_help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Lumia Rumble Recruitment Bot",
            description="A specialized bot for connecting players and teams.",
            color=discord.Color.blue()
        )
        embed.add_field(name="/lft", value="Opens your dashboard in DMs to update or delete your profile.", inline=False)
        embed.add_field(name="/lfp [query]", value="Search the database for players (e.g., Tank, Alonso).", inline=False)
        embed.set_footer(text="Use the DELETE button in /lft to remove yourself once you find a team!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Recruitment(bot))
