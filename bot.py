import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import requests

# Load environment variables
load_dotenv()

# Bot token and USDA API key
TOKEN = os.getenv("DISCORD_TOKEN")
USDA_API_KEY = os.getenv("USDA_API_KEY")

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.command()
async def macros(ctx, *, food_item: str):
    """Fetch macronutrient information for a given food item using USDA API."""
    api_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": food_item,
        "pageSize": 1,  # Get the first result
        "api_key": USDA_API_KEY
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    # Check if there are results
    if "foods" in data and data["foods"]:
        food_name = data["foods"][0]["description"]
        nutrients = data["foods"][0].get("foodNutrients", [])

        # Extract macronutrient information
        calories = next(
            (nutrient["value"] for nutrient in nutrients if nutrient["nutrientName"] == "Energy"), "N/A"
        )
        protein = next(
            (nutrient["value"] for nutrient in nutrients if nutrient["nutrientName"] == "Protein"), "N/A"
        )
        carbs = next(
            (nutrient["value"] for nutrient in nutrients if nutrient["nutrientName"] == "Carbohydrate, by difference"), "N/A"
        )
        fats = next(
            (nutrient["value"] for nutrient in nutrients if nutrient["nutrientName"] == "Total lipid (fat)"), "N/A"
        )

        # Send the macros to Discord
        await ctx.send(
            f"**{food_name}**:\n"
            f"- Calories: {calories} kcal\n"
            f"- Protein: {protein} g\n"
            f"- Carbohydrates: {carbs} g\n"
            f"- Fat: {fats} g"
        )
    else:
        await ctx.send(f"Sorry, I couldn't find nutrition info for '{food_item}'.")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    """Shutdown the bot."""
    await ctx.send("Shutting down...")
    await bot.close()

# Run the bot
bot.run(TOKEN)
