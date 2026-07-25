# A task manager discord bot under construction.

import discord
import os
import sys
import weather
import json
from datetime import date



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

tasks = []  # Shared tasks list


@client.event
async def add_task(ctx):
    await ctx.send("Enter your Task Title:")
    title = await on_message.wait_for("message", timeout=60.0)
    await ctx.send("Enter your Task Description:")
    description = await on_ready.wait_for("message", timeout=60.0)
    tasks.append({"Task Title": title.content, "Task Description": description.content})
    await ctx.send("\u2713 Task created successfully.")


@client.event
async def view_tasks(ctx):
    if tasks:
        response = "Available Tasks:\n"
        for idx, task in enumerate(tasks, start=1):
            response += f"{idx}. Task Title: {task['Task Title']}, Task Description: {task['Task Description']}\n"
        await ctx.send(response)
    else:
        await ctx.send("No Tasks Available.")


@client.event
async def update_task(ctx):
    await view_tasks(ctx)  # Show current tasks
    if tasks:
        await ctx.send("Provide the Index of the task to update:")
        try:
            index_msg = await on_message.wait_for("message", timeout=60.0)
            index = int(index_msg.content) - 1
            if 0 <= index < len(tasks):
                await ctx.send(
                    "Provide a new title or (type 'skip' to keep current title):"
                )
                new_title_msg = await on_message.wait_for("message", timeout=60.0)
                await ctx.send(
                    "Provide a new description or (type 'skip' to keep current description):"
                )
                new_desc_msg = await on_message.wait_for("message", timeout=60.0)

                if new_title_msg.content.lower() != "skip":
                    tasks[index]["Task Title"] = new_title_msg.content
                if new_desc_msg.content.lower() != "skip":
                    tasks[index]["Task Description"] = new_desc_msg.content

                await ctx.send("Task updated successfully.")
            else:
                await ctx.send("Invalid index.")
        except ValueError:
            await ctx.send("Invalid input. Please enter a number.")
        except on_message.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
    else:
        await ctx.send("No Tasks Available.")


@client.event
async def delete_task(ctx):
    await view_tasks(ctx)  # Show current tasks
    if tasks:
        await ctx.send("Provide the Index of the task to delete:")
        try:
            index_msg = await on_message.wait_for("message", timeout=60.0)
            index = int(index_msg.content) - 1
            if 0 <= index < len(tasks):
                deleted_task = tasks.pop(index)
                await ctx.send(
                    f"Task '{deleted_task['Task Title']}' deleted successfully."
                )
            else:
                await ctx.send("Invalid index.")
        except ValueError:
            await ctx.send("Invalid input. Please enter a number.")

    else:
        await ctx.send("No Tasks Available.")


def isPrime(number: int) -> bool:
    if number <= 1:
        return False

    if number == 2:
        return True

    for i in range(2, number):
        if number % i == 0:

            return False

    return True


assert isPrime(2) is True
assert isPrime(7) is True
assert isPrime(1) is False
assert isPrime(0) is False
assert isPrime(-5) is False
assert isPrime(16_937) is True

#Below code unrelated to the prime number function, but is related to the Disney trip date feature.

# The file where the Disney trip date will be saved.
DISNEY_DATE_FILE = "disney_date.json"


def save_disney_date(trip_date: date) -> None:
    """
    Saves the Disney trip date to a JSON file.

    isoformat() converts the date into:
    YYYY-MM-DD
    """

    date_data = {
        "trip_date": trip_date.isoformat()
    }

    with open(DISNEY_DATE_FILE, "w") as file:
        json.dump(date_data, file, indent=4)


def load_disney_date():
    """
    Loads the Disney trip date from the JSON file.

    Returns None if a date has not been saved yet.
    """

    try:
        with open(DISNEY_DATE_FILE, "r") as file:
            date_data = json.load(file)

        # Convert the saved text back into a date object.
        return date.fromisoformat(date_data["trip_date"])

    except FileNotFoundError:
        # The file does not exist yet.
        return None

    except (KeyError, ValueError, json.JSONDecodeError):
        # The file exists, but its contents are invalid.
        return None



@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):

    # Prevent the bot from responding to its own messages.
    if message.author == client.user:
        return

    # Remove extra spaces from the beginning and end.
    content = message.content.strip()

    if content.startswith("$hello"):
        await message.channel.send("Hello!")

    elif content.startswith("$best"):
        await message.channel.send("Chou is the best!")

    elif content.startswith("$prime"):
        prime_str = content[6:].strip()

        try:
            prime_int = int(prime_str)
            result = isPrime(prime_int)
            await message.channel.send(result)

        except ValueError:
            await message.channel.send(
                f'Sorry, "{prime_str}" is not a valid number. Try again.'
            )

    elif content.startswith("$weather"):
        weather_str = content[8:].strip()

        rawGeoCodeInfo = await weather.getRawGeoCodeInfo(weather_str)

        cleanGeoCodeInfo = await weather.getCleanGeoCodeInfo(
            rawGeoCodeInfo
        )

        rawWeatherInfo = await weather.getRawWeatherInfo(
            cleanGeoCodeInfo.lat,
            cleanGeoCodeInfo.long
        )

        weather_result = await weather.getCleanWeatherInfo(
            rawWeatherInfo
        )

        await message.channel.send(weather_result)

    # Set the Disney trip date.
    # Example: $setdisney 2026-12-15
    elif content.lower().startswith("$setdisney"):
        parts = content.split(maxsplit=1)

        # Check whether the user included a date.
        if len(parts) < 2:
            await message.channel.send(
                "Please include your Disney trip date.\n"
                "Example: `$setdisney 2026-12-15`"
            )
            return

        date_text = parts[1].strip()

        try:
            # Convert YYYY-MM-DD text into a Python date.
            trip_date = date.fromisoformat(date_text)

            # Do not allow a date that has already passed.
            if trip_date < date.today():
                await message.channel.send(
                    "That date has already passed. "
                    "Please enter a future date."
                )
                return

            # Save the date to disney_date.json.
            save_disney_date(trip_date)

            # Change the date into a readable format.
            readable_date = trip_date.strftime("%B %d, %Y")

            await message.channel.send(
                f"🏰 Disney trip date set to "
                f"**{readable_date}**! ✨"
            )

        except ValueError:
            await message.channel.send(
                "That is not a valid date.\n"
                "Please use `YYYY-MM-DD`.\n"
                "Example: `$setdisney 2026-12-15`"
            )

    # Display the Disney countdown.
    elif content.lower() == "$disney":
        trip_date = load_disney_date()

        # No date has been saved yet.
        if trip_date is None:
            await message.channel.send(
                "A Disney trip date has not been set yet.\n"
                "Use `$setdisney YYYY-MM-DD` to set one."
            )
            return

        today = date.today()
        days_left = (trip_date - today).days
        readable_date = trip_date.strftime("%B %d, %Y")

        if days_left > 1:
            response = (
                f"🏰 **{days_left} days until Disney!** ✨\n"
                f"Trip date: **{readable_date}**"
            )

        elif days_left == 1:
            response = (
                "🏰 **Only 1 day until Disney!** "
                "Start packing! ✨\n"
                f"Trip date: **{readable_date}**"
            )

        elif days_left == 0:
            response = (
                "🎉 **Today is Disney day!** "
                "Have a magical trip! 🏰"
            )

        else:
            response = (
                f"The Disney trip was scheduled for "
                f"**{readable_date}**.\n"
                "Set a new date with `$setdisney YYYY-MM-DD`."
            )

        await message.channel.send(response)

        if __name__ == "__main__":
                token = os.getenv("CUSPYDO_TOKEN")

    if not token:
        print(
            f"token value is {token}. "
            "Did you forget to 'source /path/to/you/.env' or 'vrun'?"
        )
        sys.exit(1)

    client.run(token)