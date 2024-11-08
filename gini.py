import discord
from discord.ext import commands
import random
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GAME_NAME = "Genie's Quest for Power"
MAX_HEALTH = 100
CHALLENGE_ATTEMPTS = 3

responses = {
    "intro": "🧞‍♂️ **Welcome, brave soul!** You've summoned the ancient Genie for an epic quest! Choose your spells wisely as you face dangerous trials. Only the worthy may reach the ultimate wish!",
    "phase1": "🧞‍♂️ **You've entered the Shadowed Forest!** The eerie silence is broken only by whispers in the wind. **Will you survive the guardians hidden in the mist?**",
    "phase2": "🧞‍♂️ **A dark cave awaits...** In its depths, lies the treasure of ancient spells. But beware, **its guardian is fierce and cunning!**",
    "phase3": "🧞‍♂️ **At the edge of the Mystic Falls...** The final trial awaits. To pass, you must master the ancient arts or be lost forever.",
    "win": "🧞‍♂️ **Well done, traveler!** You've bested this challenge with style.",
    "lose": "🧞‍♂️ **Alas, your spell missed its mark.** You have {attempts} attempts left before the trial is lost.",
    "revive": "🧞‍♂️ **A second chance!** I grant you another breath to continue the quest.",
    "final": "🧞‍♂️ **Incredible! You've survived all trials.** Now, it's time to choose your ultimate destiny.",
    "wish": "🧞‍♂️ **Your wish shall be granted!** Witness the magic unfold...",
}

phases = [
    {
        "name": "Shadowed Forest",
        "description": responses["phase1"],
        "spells": [
            {
                "name": "Fireball 🔥",
                "success": 0.5,
                "animation": "The Genie hurls a fireball, illuminating the dark forest as it blazes through the shadows!",
            },
            {
                "name": "Ice Blast 🧊",
                "success": 0.6,
                "animation": "An icy chill fills the air as shards of ice fly, freezing everything in their path.",
            },
            {
                "name": "Invisibility 🕶️",
                "success": 0.7,
                "animation": "You vanish into the shadows, sneaking past the unseen dangers.",
            },
        ],
    },
    {
        "name": "Dark Cave",
        "description": responses["phase2"],
        "spells": [
            {
                "name": "Lightning ⚡",
                "success": 0.6,
                "animation": "Lightning crackles as it strikes, illuminating the cave’s stone walls.",
            },
            {
                "name": "Stone Shield 🛡️",
                "success": 0.5,
                "animation": "A shield of rock rises, guarding against the guardian’s ferocious attack!",
            },
            {
                "name": "Healing 🌟",
                "success": 0.5,
                "animation": "A soft light surrounds you, restoring your strength in this dark place.",
            },
        ],
    },
    {
        "name": "Mystic Falls",
        "description": responses["phase3"],
        "spells": [
            {
                "name": "Earthquake 🌍",
                "success": 0.6,
                "animation": "The ground shakes violently, forcing the guardian back!",
            },
            {
                "name": "Wind Gust 💨",
                "success": 0.7,
                "animation": "A powerful gust of wind surges forward, knocking enemies off balance.",
            },
            {
                "name": "Mind Control 🧠",
                "success": 0.4,
                "animation": "You reach out, attempting to bend the guardian’s will to your command.",
            },
        ],
    },
]

final_wishes = [
    {
        "name": "Ruler of Realms 👑",
        "animation": """
**A golden crown appears above your head.** The Genie bows, declaring you the ruler of realms, granting dominion over all lands and creatures.
""",
    },
    {
        "name": "Master of Elements 🌊🔥",
        "animation": """
**The Genie’s eyes sparkle as flames, water, and winds swirl around you.** You now wield the power of the elements themselves!
""",
    },
    {
        "name": "Time Weaver ⏳",
        "animation": """
**A glowing hourglass appears in your hand.** You can now shape time, bending past and future to your will!
""",
    },
]


async def play_animation(ctx, text):
    for line in text.split("\n"):
        if line.strip():  # Avoid sending empty lines
            await ctx.send(line)
            await asyncio.sleep(2)


@bot.event
async def on_ready():
    print(f"🧞‍♂️ {GAME_NAME} is ready! Logged in as {bot.user}")


@bot.command(name="gini")
async def start_game(ctx):
    user = ctx.author
    health = MAX_HEALTH
    attempts = CHALLENGE_ATTEMPTS

    await play_animation(ctx, responses["intro"])

    for phase in phases:
        await play_animation(ctx, phase["description"])
        await ctx.send(f"**Entering {phase['name']}...**")

        while attempts > 0:
            spell = await get_spell(ctx, phase["spells"])
            if spell is None:
                return
            success = random.random() < next(
                s["success"] for s in phase["spells"] if s["name"] == spell
            )

            if success:
                health += 10
                await play_animation(ctx, responses["win"])
                await play_animation(
                    ctx,
                    [s["animation"] for s in phase["spells"] if s["name"] == spell][0],
                )
                break
            else:
                health -= 20
                attempts -= 1
                await play_animation(ctx, responses["lose"].format(attempts=attempts))

        if attempts == 0:
            await play_animation(ctx, responses["revive"])
            health = MAX_HEALTH
            attempts = CHALLENGE_ATTEMPTS

    await play_animation(ctx, responses["final"])

    final_wish = await get_final_wish(ctx)
    if final_wish is not None:
        await play_animation(ctx, responses["wish"])
        await play_animation(ctx, final_wish["animation"])
        await ctx.send("**An epic adventure, well-deserved!**")


async def get_spell(ctx, spells):
    spell_options = "\n".join(f"{i+1}. {s['name']}" for i, s in enumerate(spells))
    await ctx.send(f"Choose your spell:\n{spell_options}")

    def check(m):
        return (
            m.author == ctx.author
            and m.content.isdigit()
            and 1 <= int(m.content) <= len(spells)
        )

    try:
        choice = await bot.wait_for("message", check=check, timeout=30.0)
        return spells[int(choice.content) - 1]["name"]
    except:
        await ctx.send("Oh no, you took too long! Let's try again.")
        return None


async def get_final_wish(ctx):
    final_wish_options = "\n".join(
        f"{i+1}. {w['name']}" for i, w in enumerate(final_wishes)
    )
    await ctx.send(f"Choose your ultimate wish:\n{final_wish_options}")

    def check(m):
        return (
            m.author == ctx.author
            and m.content.isdigit()
            and 1 <= int(m.content) <= len(final_wishes)
        )

    try:
        choice = await bot.wait_for("message", check=check, timeout=60.0)
        return final_wishes[int(choice.content) - 1]
    except:
        await ctx.send("Time’s up! Next time, adventurer.")
        return None


bot.run(TOKEN)
