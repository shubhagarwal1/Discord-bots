import discord

discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.dylib")

from discord.ext import commands
import random
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("HARRY_TOKEN")  # Use HARRY_TOKEN from .env

# Set up the bot with Message Content Intent
intents = discord.Intents.default()
intents.message_content = (
    True  # Enable message content intent for command functionality
)
bot = commands.Bot(command_prefix="!", intents=intents)

# Sorting Hat Functionality
houses = ["Gryffindor 🦁", "Hufflepuff 🦡", "Ravenclaw 🦅", "Slytherin 🐍"]
quotes = [
    "It does not do to dwell on dreams and forget to live. – Albus Dumbledore",
    "I solemnly swear that I am up to no good. – Harry Potter",
    "We’ve all got both light and dark inside us. What matters is the part we choose to act on. – Sirius Black",
    "Happiness can be found, even in the darkest of times, if one only remembers to turn on the light. – Albus Dumbledore",
]

spells = {
    "Expelliarmus": "Disarms your opponent.",
    "Lumos": "Creates light at the tip of the wand.",
    "Alohomora": "Unlocks doors.",
    "ExpectoPatronum": "Summons a Patronus to defend against Dementors.",
    "WingardiumLeviosa": "Levitates objects.",
    "Stupefy": "Stuns your opponent.",
}


# Bot Commands
@bot.event
async def on_ready():
    print(f"HogwartsBot is ready! Logged in as {bot.user}")


@bot.event
async def on_message(message):
    # Log incoming messages for debugging
    print(f"Message from {message.author}: {message.content}")

    # Ensure the bot processes commands
    await bot.process_commands(message)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")  # Simple test command to check bot response


@bot.command(name="sort")
async def sort_house(ctx):
    # Check if the author is in a voice channel
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel for me to sort you!")
        return

    # Get the voice channel of the user
    voice_channel = ctx.author.voice.channel

    # Join the user's voice channel
    voice_client = await voice_channel.connect()

    try:
        # Choose a random house and send a message
        house = random.choice(houses)
        await ctx.send(
            f"{ctx.author.mention}, the Sorting Hat has placed you in **{house}**!"
        )

        # Play the audio file (replace 'sorting_audio.mp3' with your local file path)
        audio_source = discord.FFmpegPCMAudio("battel_of_hogwartz.mp3")
        if not voice_client.is_playing():
            voice_client.play(audio_source)

            # Wait until the audio finishes playing
            while voice_client.is_playing():
                await asyncio.sleep(1)

    finally:
        # Disconnect from the voice channel after playing
        await voice_client.disconnect()


@bot.command(name="quote")
async def random_quote(ctx):
    quote = random.choice(quotes)
    await ctx.send(f"✨ *{quote}* ✨")


@bot.command(name="spell")
async def cast_spell(ctx, spell_name: str):
    spell_name = spell_name.capitalize()
    if spell_name in spells:
        await ctx.send(f"🔮 **{spell_name}** – {spells[spell_name]}")
    else:
        await ctx.send(
            "Hmm, I don't recognize that spell. Are you sure you're a wizard?"
        )


@bot.command(name="help_hogwarts")
async def help(ctx):
    help_text = """
    **Welcome to HogwartsBot!** Here are my commands:
    - `!sort`: Get sorted into a Hogwarts House.
    - `!quote`: Receive a random quote from the Harry Potter universe.
    - `!spell <spell name>`: Get information on a specific spell (e.g., `!spell Lumos`).
    - `!help_hogwarts`: Show this help message.
    - `!ping`: Check if the bot is responding.
    """
    await ctx.send(help_text)


bot.run(TOKEN)
