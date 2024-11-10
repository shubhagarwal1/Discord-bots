import discord
import time

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
houses = ["Gryffindor 🧑‍🐎", "Hufflepuff 🦡", "Ravenclaw 🦅", "Slytherin 🐍"]
house_audio_files = {
    "Gryffindor 🧑‍🐎": "gryffindor.mp3",
    "Hufflepuff 🦡": "hufflepuff.mp3",
    "Ravenclaw 🦅": "ravenclaw.mp3",
    "Slytherin 🐍": "slytherin.mp3",
}
quotes = [
    "It does not do to dwell on dreams and forget to live. – Albus Dumbledore",
    "I solemnly swear that I am up to no good. – Harry Potter",
    "We’ve all got both light and dark inside us. What matters is the part we choose to act on. – Sirius Black",
    "Happiness can be found, even in the darkest of times, if one only remembers to turn on the light. – Albus Dumbledore",
]
#
spells = {
    "Expelliarmus": {"cost": 10, "damage": 15},
    "Lumos": {"cost": 5, "damage": 5},
    "Alohomora": {"cost": 8, "damage": 10},
    "expectro": {"cost": 20, "damage": 25},
    "WingardiumLeviosa": {"cost": 12, "damage": 18},
    "Stupefy": {"cost": 15, "damage": 20},
}
user_data = {}


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
    # Check if the command was issued in a voice channel
    user = ctx.author
    if ctx.author.voice is None:
        await ctx.send(
            "Please join a voice channel and then use the `!sort` command so I can sort you into a house!"
        )
        return

    # Get the user's voice channel
    voice_channel = ctx.author.voice.channel

    # Join the user's voice channel
    voice_client = await voice_channel.connect()

    try:
        # # Play intro audio
        # audio_source = discord.FFmpegPCMAudio("intro1.mp3")
        # if not voice_client.is_playing():
        #     voice_client.play(audio_source)
        #     # Wait until the audio finishes playing
        #     while voice_client.is_playing():
        #         await asyncio.sleep(1)

        # Choose a random house and send a message
        house = random.choice(houses)
        user_data[user.id] = {
            "house": house,
            "points": 100,
            "spells": ["Lumos", "expectro", "Stupefy", "WingardiumLeviosa"],
            "last_claim": "",
        }

        await ctx.send(
            f"{user.mention}, the Sorting Hat has placed you in **{house}**! You start with 100 points."
        )

        # Play the house-specific audio
        house_audio = house_audio_files[house]
        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(house_audio))
            # Wait until the house audio finishes playing
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


@bot.command(name="my")
async def user_profile(ctx):
    user = ctx.author
    if user.id not in user_data:
        await ctx.send(
            "You need to be sorted first! Use `!sort` to get sorted into a house."
        )
        return

    house = user_data[user.id]["house"]
    points = user_data[user.id]["points"]
    spells_learned = user_data[user.id]["spells"]
    spells_text = ", ".join(spells_learned) if spells_learned else "None"

    profile_message = (
        f"**{user.mention}'s Profile**\n"
        f"House: **{house}**\n"
        f"Points: **{points}**\n"
        f"Learned Spells: **{spells_text}**"
    )
    await ctx.send(profile_message)


@bot.command(name="learn_spell")
async def learn_spell(ctx, spell_name: str = None):
    user = ctx.author

    try:
        # Check if the user has been sorted
        if user.id not in user_data:
            await ctx.send(
                "You need to be sorted first! Use `!sort` to get sorted into a house."
            )
            return

        # Check if a spell name was provided
        if not spell_name:
            await ctx.send(
                "Please provide a spell name to learn. Example: `!learn_spell lumos`"
            )
            return

        # Capitalize the spell name and validate it
        spell_name = spell_name.capitalize()
        if " " in spell_name or spell_name not in spells:
            await ctx.send("That spell does not exist. Please choose a valid spell.")
            return

        # Check if user has enough points to learn the spell
        spell_cost = spells[spell_name]["cost"]
        if user_data[user.id]["points"] < spell_cost:
            await ctx.send(
                f"You don't have enough points to learn **{spell_name}**. It costs {spell_cost} points."
            )
            return

        # Check if the user already knows the spell
        if spell_name in user_data[user.id]["spells"]:
            await ctx.send(f"You already know **{spell_name}**!")
            return

        # Deduct points and add the spell to the user's known spells
        user_data[user.id]["points"] -= spell_cost
        user_data[user.id]["spells"].append(spell_name)

        await ctx.send(
            f"{user.mention} has learned the spell **{spell_name}**! It cost {spell_cost} points. You now have {user_data[user.id]['points']} points."
        )

    except KeyError as e:
        await ctx.send(
            f"An error occurred: Missing data for key `{e}`. Please try again."
        )
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")


@bot.command(name="duel")
async def duel(ctx, opponent: discord.Member = None):
    user = ctx.author

    try:
        # If no opponent is provided, duel against the bot itself
        if not opponent:
            opponent = ctx.guild.me  # Bot as the opponent

        # Initialize data for the bot if it doesn't exist
        if opponent.id == ctx.guild.me.id and opponent.id not in user_data:
            # Assign default values for the bot
            user_data[opponent.id] = {
                "house": "BotHouse",
                "points": 1000,
                "spells": ["Lumos", "expectro", "Stupefy"],
            }

        # Check if both participants are sorted
        if user.id not in user_data or opponent.id not in user_data:
            await ctx.send(
                "Both participants need to be sorted first! Use `!sort` to get sorted into a house."
            )
            return

        # Check if both participants have learned at least one spell
        if not user_data[user.id]["spells"] or not user_data[opponent.id]["spells"]:
            await ctx.send(
                "Both participants need to have learned at least one spell to duel! Use `!learn_spell` to learn a spell."
            )
            return

        # Ask the user to cast their spell (without showing options)
        await ctx.send(
            f"**{user.mention}**, cast your spell by typing the name of the spell you wish to use."
        )

        def check(msg):
            return msg.author == user and msg.content in user_data[user.id]["spells"]

        try:
            user_msg = await bot.wait_for("message", timeout=30.0, check=check)
            user_spell = user_msg.content
            await ctx.send(f"**{user.mention}** casts **{user_spell}**!")
        except asyncio.TimeoutError:
            await ctx.send(
                "You took too long to cast your spell! The duel is canceled."
            )
            return
        except ValueError:
            await ctx.send("That's not a valid spell. Duel canceled.")
            return

        # Select random spell for the opponent (bot or user) without revealing it
        opponent_spell = random.choice(user_data[opponent.id]["spells"])

        # Both players cast their spells without revealing the spells to each other
        await ctx.send(f"**{opponent.mention}** casts {opponent_spell} spell!")

        # Calculate damage
        user_damage = spells[user_spell]["damage"] + random.randint(-5, 5)
        opponent_damage = spells[opponent_spell]["damage"] + random.randint(-5, 5)

        # Deduct the damage from each participant's points
        user_data[user.id]["points"] -= opponent_damage
        user_data[opponent.id]["points"] -= user_damage

        await ctx.send(f"**{user.mention}** deals **{user_damage}** damage!")
        await ctx.send(f"**{opponent.mention}** deals **{opponent_damage}** damage!")

        # Check if points have fallen below zero and set to zero if necessary
        if user_data[user.id]["points"] < 0:
            user_data[user.id]["points"] = 0
        if opponent.id != ctx.guild.me.id and user_data[opponent.id]["points"] < 0:
            user_data[opponent.id]["points"] = 0

        # Remove used spells
        user_data[user.id]["spells"].remove(user_spell)
        if opponent.id != ctx.guild.me.id:
            user_data[opponent.id]["spells"].remove(opponent_spell)

        # Determine the winner and update points
        if user_damage > opponent_damage:
            await ctx.send(
                f"**{user.mention}** wins the duel and earns 20 points for **{user_data[user.id]['house']}**!"
            )
            user_data[user.id]["points"] += 20
        elif opponent_damage > user_damage:
            await ctx.send(
                f"**{opponent.mention}** wins the duel and earns 20 points for **{user_data[opponent.id]['house']}**!"
            )
            if opponent.id != ctx.guild.me.id:
                user_data[opponent.id]["points"] += 20
        else:
            await ctx.send("It's a tie! No points awarded.")

        # Display updated points
        await ctx.send(
            f"**{user.mention}'s** updated points: {user_data[user.id]['points']}."
        )
        if opponent.id != ctx.guild.me.id:
            await ctx.send(
                f"**{opponent.mention}'s** updated points: {user_data[opponent.id]['points']}."
            )

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")


@bot.command(name="earn")
async def earn_points(ctx):
    user = ctx.author

    if user.id not in user_data:
        await ctx.send(
            "You need to be sorted first! Use `!sort` to get sorted into a house."
        )
        return

    # Get the current time in seconds
    current_time = time.time()

    # Check if the user has already claimed points recently
    if "last_claim" in user_data[user.id]:
        last_claim_time = user_data[user.id]["last_claim"]

        # Ensure that last_claim_time is a float and not a string
        if isinstance(last_claim_time, str):
            try:
                last_claim_time = float(last_claim_time)
                user_data[user.id][
                    "last_claim"
                ] = last_claim_time  # Update the value if it was string
            except ValueError:
                # If it can't be converted to float, set it to 0 to allow immediate claim
                last_claim_time = 0

        time_since_last_claim = current_time - last_claim_time

        # If less than 1 hour has passed (3600 seconds), deny the claim
        if time_since_last_claim < 3600:
            remaining_time = 3600 - time_since_last_claim
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            await ctx.send(
                f"You can claim points again in {int(minutes)}m {int(seconds)}s."
            )
            return

    # Points earned
    points_earned = random.randint(10, 30)
    user_data[user.id]["points"] += points_earned

    # Update last claim time to the current time
    user_data[user.id]["last_claim"] = current_time

    # Send the points earned message
    await ctx.send(
        f"{user.mention}, you have earned {points_earned} points! You now have {user_data[user.id]['points']} points."
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
