import discord
from discord import app_commands
from deep_translator import GoogleTranslator
from datetime import datetime

def setup(tree):
    # translate code
    @tree.command(name="translate", description="Translate into a diff lang")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def translate(interaction: discord.Interaction, lang: str, *, text: str):
        """
        Example:
        /translate lang: es text: hello
        """
        now = datetime.now().strftime("%b %d, %Y %H:%M%p")
        user = interaction.user
        username = user.name
        
        try:
            translated = GoogleTranslator(source="auto", target=lang).translate(text)
            await interaction.response.send_message(translated)
            
            print(f"[{now}] ✅ {username} translated to '{lang}' | text: '{text}'")
            
        except Exception as e:
            await interaction.response.send_message(
                "Error, check your language code (ISO 639, 2 character language code required. Case sensitive.)."
            )
            print(f"[{now}] ❌ {username} tried lang='{lang}'")