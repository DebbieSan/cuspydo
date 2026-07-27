# A task manager discord bot under construction.

import discord
import os
import sys
import weather
import json
from datetime import date
from pathlib import Path



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

#Prime number checker - this was what got the bot started!

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

#weather functions - these are in a separate file, but are imported here.

# Unit words accepted by the weather command.
WEATHER_UNITS = {
    "c": "c",
    "celsius": "c",
    "f": "f",
    "fahrenheit": "f"
}


# Weather feature words accepted by the command.
WEATHER_FEATURES = {
    "summary": "summary",
    "conditions": "conditions",
    "temp": "temperature",
    "temperature": "temperature",
    "feels": "feels",
    "humidity": "humidity",
    "wind": "wind",
    "rain": "rain",
    "precipitation": "rain",
    "clouds": "clouds",
    "pressure": "pressure",
    "all": "all"
}


def parseWeatherCommand(content: str):
    """
    Separate a weather command into:

    location
    temperature unit
    requested weather features

    Example:
        $weather New York f wind humidity
    """

    # Remove "$weather" and split the remaining words.
    arguments = content[len("$weather"):].strip().split()

    if not arguments:
        raise ValueError(
            "Please include a location.\n"
            "Example: `$weather Calgary f all`"
        )

    # Celsius is the default.
    unit = "c"

    features = []

    valid_options = (
        set(WEATHER_UNITS) |
        set(WEATHER_FEATURES)
    )

    # Read weather options from the end of the command.
    #
    # In:
    # $weather New York f wind
    #
    # "wind" and "f" are options.
    # "New York" remains the location.
    while (
        arguments and
        arguments[-1].lower() in valid_options
    ):
        option = arguments.pop().lower()

        if option in WEATHER_UNITS:
            unit = WEATHER_UNITS[option]

        else:
            feature = WEATHER_FEATURES[option]

            if feature not in features:
                features.append(feature)

    location = " ".join(arguments).strip()

    if not location:
        raise ValueError(
            "Please include a location before "
            "the weather options."
        )

    # Display the basic summary when no feature is specified.
    if not features:
        features = ["summary"]

    return location, unit, features

#Disney Countdown

# This creates disney_date.json beside this Python file.
DISNEY_DATE_FILE = Path(
    os.getenv(
        "DISNEY_DATE_FILE",
        str(Path(__file__).resolve().parent / "disney_date.json"),
    )
)

def save_disney_date(trip_date: date) -> None:
    """
    Save the Disney trip date to disney_date.json.
    """

    date_data = {
        "trip_date": trip_date.isoformat()
    }

    with open(DISNEY_DATE_FILE, "w", encoding="utf-8") as file:
        json.dump(date_data, file, indent=4)


def load_disney_date():
    """
    Load the Disney trip date.

    Returns None when the file does not exist or contains invalid data.
    """

    try:
        with open(DISNEY_DATE_FILE, "r", encoding="utf-8") as file:
            date_data = json.load(file)

        return date.fromisoformat(date_data["trip_date"])

    except FileNotFoundError:
        return None

    except (KeyError, ValueError, json.JSONDecodeError):
        return None


def calculate_disney_countdown(
    trip_date: date,
    current_date: date | None = None
) -> tuple[int, str]:
    """
    Calculate the Disney countdown.

    current_date is optional. Tests can provide a fake current date.
    The actual Discord command uses today's real date.
    """

    if current_date is None:
        current_date = date.today()

    days_left = (trip_date - current_date).days
    readable_date = trip_date.strftime("%B %d, %Y")

    if days_left > 1:
        response = (
            f"🏰 **{days_left} days until Disney!** ✨\n"
            f"Trip date: **{readable_date}**"
        )

    elif days_left == 1:
        response = (
            "🏰 **Only 1 day until Disney!** Start packing! ✨\n"
            f"Trip date: **{readable_date}**"
        )

    elif days_left == 0:
        response = (
            "🎉 **Today is Disney day!** "
            "Have a magical trip! 🏰"
        )

    else:
        response = (
            f"The Disney trip date was **{readable_date}**.\n"
            "Set a new date with `$setdisney YYYY-MM-DD`."
        )

    return days_left, response


def test_disney_countdown() -> None:
    """
    Test the countdown using fake dates.

    These tests do not depend on today's actual date.
    """

    trip_date = date(2026, 12, 15)

    # Test when the trip is 10 days away.
    days_left, message = calculate_disney_countdown(
        trip_date,
        date(2026, 12, 5)
    )

    assert days_left == 10
    assert "10 days until Disney" in message

    # Test when the trip is tomorrow.
    days_left, message = calculate_disney_countdown(
        trip_date,
        date(2026, 12, 14)
    )

    assert days_left == 1
    assert "Only 1 day" in message

    # Test Disney day.
    days_left, message = calculate_disney_countdown(
        trip_date,
        date(2026, 12, 15)
    )

    assert days_left == 0
    assert "Today is Disney day" in message

    # Test after the trip.
    days_left, message = calculate_disney_countdown(
        trip_date,
        date(2026, 12, 16)
    )

    assert days_left == -1
    assert "Set a new date" in message

    print("All Disney countdown tests passed!")


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    # Prevent the bot from responding to its own messages
    if message.author == client.user:
        return

    # Remove extra spaces and make command checking case-insensitive
    command = message.content.strip().lower()

    # Display the help menu
    if command == "$help":
        help_embed = discord.Embed(
            title="Cuspydo Help",
            description="Here are the commands currently available:",
            color=0xD4A72C
        )

        help_embed.add_field(
            name="$hello",
            value="Cuspydo says hello!",
            inline=False
        )

        help_embed.add_field(
            name="$best",
            value="Find out who Cuspydo thinks is the best.",
            inline=False
        )

        help_embed.add_field(
            name="$prime <number>",
            value="Checks whether a number is a prime number.\nExample: `$prime 17`",
            inline=False
        )

        help_embed.add_field(
            name="$weather <location> [c|f] [features]",
            value=(
        "Shows current weather for a location.\n\n"
        "**Features:**\n"
        "`conditions`, `temp`, `feels`, `humidity`, "
        "`wind`, `rain`, `clouds`, `pressure`, `all`\n\n"
        "**Examples:**\n"
        "`$weather Banff`\n"
        "`$weather Jasper f`\n"
        "`$weather Jasper c humidity`\n"
        "`$weather New York f wind pressure`\n"
        "`$weather Anaheim c all`"
         ),
        inline=False
        )


        help_embed.add_field(
            name="$setdisney",
            value="Sets the date for your upcoming Disney trip.",
            inline=False
        )

        help_embed.add_field(
            name="$disney",
            value="Shows the countdown to your upcoming Disney trip.",
            inline=False
        )


        help_embed.add_field(
            name="$help",
            value="Displays this list of commands.",
            inline=False
        )

        help_embed.set_footer(
            text="Cuspydo • More features coming soon!"
        )

        await message.channel.send(embed=help_embed)



    
    content = message.content.strip()
    command = content.lower()

    if command == "$version":
        await message.channel.send("Bot version: help 26.7.0")
        return

    if command == "$hello":
        await message.channel.send("Hello!")

    elif command == "$best":
        await message.channel.send("Chou is the best!")

    if command == "$who":
            await message.channel.send("I am Cuspydo!I am the cutest bot on discord! I can help you with tasks, check prime numbers, and even give you the weather! Type $help to see what I can do!")

    elif command.startswith("$prime"):
        prime_str = content[6:].strip()

        try:
            prime_int = int(prime_str)
            result = isPrime(prime_int)
            await message.channel.send(str(result))

        except ValueError:
            await message.channel.send(
                f'Sorry, "{prime_str}" is not a valid number. Try again.'
            )

    # weather section

    elif (
        command == "$weather"
        or command.startswith("$weather ")
    ):
        try:
            # Separate the location, unit, and requested features.
            weather_str, unit, features = parseWeatherCommand(
                content
            )

            rawGeoCodeInfo = await weather.getRawGeoCodeInfo(
                weather_str
            )

            cleanGeoCodeInfo = await weather.getCleanGeoCodeInfo(
                rawGeoCodeInfo
            )

            # Pass the requested C/F unit to Open-Meteo.
            rawWeatherInfo = await weather.getRawWeatherInfo(
                cleanGeoCodeInfo.lat,
                cleanGeoCodeInfo.long,
                unit
            )

            # Format only the requested features.
            weather_result = await weather.getCleanWeatherInfo(
                rawWeatherInfo,
                weather_str,
                unit,
                features
            )

            await message.channel.send(weather_result)

        except ValueError as error:
            # Friendly errors, such as an unknown location.
            await message.channel.send(str(error))

        except Exception as error:
            # This full error will appear in systemd logs.
            print(f"Weather command error: {error}")

            await message.channel.send(
                "I couldn't retrieve the weather right now."
            )

    # Example:
    # $setdisney 2026-12-15
    elif command.startswith("$setdisney"):
        parts = content.split(maxsplit=1)

        if len(parts) < 2:
            await message.channel.send(
                "Please include a date.\n"
                "Example: `$setdisney 2026-12-15`"
            )
            return

        date_text = parts[1].strip()

        try:
            trip_date = date.fromisoformat(date_text)

            if trip_date < date.today():
                await message.channel.send(
                    "That date has already passed. "
                    "Please enter a future date."
                )
                return

            save_disney_date(trip_date)

            readable_date = trip_date.strftime("%B %d, %Y")

            await message.channel.send(
                f"🏰 Disney trip date set to "
                f"**{readable_date}**! ✨"
            )

        except ValueError:
            await message.channel.send(
                "That is not a valid date.\n"
                "Use the format `YYYY-MM-DD`.\n"
                "Example: `$setdisney 2026-12-15`"
            )

        except Exception as error:
            traceback.print_exc()

            await message.channel.send(
                "Something went wrong while saving the date.\n"
                f"Error: `{type(error).__name__}: {error}`"
            )

    # Show the countdown.
    elif content.lower() == "$disney":
        try:
            trip_date = load_disney_date()

            if trip_date is None:
                await message.channel.send(
                    "I could not find a saved Disney date.\n"
                    "Set one with `$setdisney YYYY-MM-DD`."
                )
                return

            days_left, response = calculate_disney_countdown(
                trip_date
            )

            await message.channel.send(response)

        except Exception as error:
            # Print the complete error in the terminal.
            traceback.print_exc()

            await message.channel.send(
                "The Disney countdown encountered an error.\n"
                f"Error: `{type(error).__name__}: {error}`"
            )

    # Diagnostic command.
    elif content.lower() == "$testdisney":
        try:
            trip_date = load_disney_date()

            test_results = [
                "📋**Disney Countdown Test**",
                f"Today: `{date.today().isoformat()}`",
                f"Save file: `{DISNEY_DATE_FILE}`",
                f"File exists: `{DISNEY_DATE_FILE.exists()}`"
            ]

            if trip_date is None:
                test_results.append("Loaded trip date: `None`")  
                test_results.append(
                    "❌ No valid Disney date was found."
                )

            else:
                days_left, response = calculate_disney_countdown(
                    trip_date
                )

                test_results.append(
                    f"Loaded trip date: `{trip_date.isoformat()}`"
                )

                test_results.append(
                    f"Calculated days left: `{days_left}`"
                )

                test_results.append(
                    "✅ The countdown calculation is working."
                )

            await message.channel.send("\n".join(test_results))

        except Exception as error:
            traceback.print_exc()

            await message.channel.send(
                "❌ The Disney test failed.\n"
                f"Error type: `{type(error).__name__}`\n"
                f"Error message: `{error}`"
            )


if __name__ == "__main__":
    # Run the automatic countdown tests first.
    test_disney_countdown()

    token = os.getenv("CUSPYDO_TOKEN")

    if not token:
        print(
            f"token value is {token}. "
            "Did you forget to 'source /path/to/you/.env' or 'vrun'?"
        )
        sys.exit(1)

    client.run(token)