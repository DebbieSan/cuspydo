# A task manager discord bot under construction.

import discord
import os
import sys
import weather
import json
import asyncio
from datetime import date
from pathlib import Path



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TODO_FILE = Path("todos.json")

def load_todos():
    if TODO_FILE.exists():
        with open(TODO_FILE, "r") as file:
            return json.load(file)

    return {}

def save_todos(todos):
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file, indent=4)

todos = load_todos()

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


# A little timer

def convert_timer_to_seconds(timer_text: str) -> int:
    """
    Convert a timer such as 10s, 5m, or 2h into seconds.

    Examples:
        10s becomes 10 seconds
        5m becomes 300 seconds
        2h becomes 7200 seconds
    """

    timer_text = timer_text.lower().strip()

    # The final character tells the unit.
    unit = timer_text[-1]

    # Everything before the final character should be the number.
    amount = int(timer_text[:-1])

    if unit == "s":
        return amount

    if unit == "m":
        return amount * 60  

    if unit == "h":
        return amount * 60 * 60

    # Raise an error if the user did not enter s, m, or h.
    raise ValueError("Invalid timer unit")


async def run_timer(message, seconds: int, timer_name: str):
    """
    Wait for the timer to finish and then notify the channel.
    """

    await asyncio.sleep(seconds)

    await message.channel.send(
        f"{message.author.mention}, your timer for {timer_name} is finished."
    )

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


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    # Prevent the bot from responding to its own messages
    if message.author == client.user:
        return
    user_id = str(message.author.id)

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
    name="$timer <duration> [description]",
    value=(
        "Starts a timer and notifies the channel when it finishes.\n"
        "Use `s` for seconds, `m` for minutes, or `h` for hours.\n\n"
        "Examples:\n"
        "`$timer 30s`\n"
        "`$timer 5m Check the oven`\n"
        "`$timer 2h Laundry`"
    ),
    inline=False
)
        help_embed.add_field(
    name="$todo",
    value=(
        "Manage your personal to-do list.\n\n"
        "**Commands:**\n"
        "`$todo add <task>` - Add a new task\n"
        "`$todo list` - Show your personal tasks\n"
        "`$todo done <number>` - Mark a task as complete\n"
        "`$todo delete <number>` - Delete a task\n\n"
        "**Examples:**\n"
        "`$todo add Study graphs`\n"
        "`$todo list`\n"
        "`$todo done 1`\n"
        "`$todo delete 2`"
    ),
    inline=False
)

        help_embed.add_field(
            name="$help",
            value="Displays this list of commands.",
            inline=False
        )

        help_embed.set_footer(
            text="Cuspydo by Debbie • More features coming soon!"
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

    elif command == "$who":
        await message.channel.send(
            "I am Cuspydo!I am the cutest bot on discord! I can help you with tasks, "
            "check prime numbers, and even give you the weather! Type $help to see "
            "what I can do!"
        )

# prime section

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

# timer section

    elif content.lower().startswith("$timer"):
        # Split the message into a maximum of three parts.
        #
        # Example:
        # "$timer 10m Check github" becomes:
        #
        # parts[0] = "$timer"
        # parts[1] = "10m"
        # parts[2] = "Check github"

        parts = message.content.split(maxsplit=2)

        # Make sure the user included a timer duration.
        if len(parts) < 2:
            await message.channel.send(
                "Please enter a timer duration.\n"
                "Examples: `$timer 10s`, `$timer 5m`, or `$timer 2h`."
            )
            return

        timer_text = parts[1]

        # Use the optional description if the user entered one.
        if len(parts) == 3:
            timer_name = parts[2]
        else:
            timer_name = timer_text

        try:
            seconds = convert_timer_to_seconds(timer_text)

        except (ValueError, IndexError):
            await message.channel.send(
                "Invalid timer format. Use `s` for seconds, `m` for minutes, "
                "or `h` for hours.\n"
                "Examples: `$timer 10s`, `$timer 5m`, or `$timer 2h`."
            )
            return

        # Prevent zero or negative timers.
        if seconds <= 0:
            await message.channel.send(
                "The timer must be longer than zero seconds."
            )
            return

        # Safety limit: 24 hours.
        if seconds > 86400:
            await message.channel.send(
                "Timers cannot be longer than 24 hours."
            )
            return

        # Confirm that the timer started.
        await message.channel.send(
            f"{message.author.mention}, your timer for {timer_name} has started. "
            f"Duration: {timer_text}."
        )

        # Start the timer as a separate background task.
        asyncio.create_task(
            run_timer(message, seconds, timer_name)
        )

        return

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


# Todo section

    elif command.startswith("$todo add "):
        task_text = message.content[len("$todo add "):].strip()

        if not task_text:
            await message.channel.send("Please include a task.")
            return

        if user_id not in todos:
            todos[user_id] = []

        todos[user_id].append({
            "task": task_text,
            "done": False
        })

        save_todos(todos)

        await message.channel.send(
            f"Added to your to-do list: **{task_text}**"
        )

    elif command == "$todo list":
        user_todos = todos.get(user_id, [])

        if not user_todos:
            await message.channel.send(
                "Your to-do list is empty."
            )
            return

        response = "**Your To-Do List**\n\n"

        for index, todo in enumerate(user_todos, start=1):
            if todo["done"]:
                status = "✅"
            else:
                status = "⬜"

            response += f"{index}. {status} {todo['task']}\n"

        await message.channel.send(response)

    elif command.startswith("$todo done "):
        task_number = message.content[len("$todo done "):].strip()

        try:
            index = int(task_number) - 1
        except ValueError:
            await message.channel.send(
                "Please enter a valid task number."
            )
            return

        user_todos = todos.get(user_id, [])

        if index < 0 or index >= len(user_todos):
            await message.channel.send(
                "That task number doesn't exist."
            )
            return

        user_todos[index]["done"] = True
        save_todos(todos)

        await message.channel.send(
            f"Completed: **{user_todos[index]['task']}**"
        )

    elif command.startswith("$todo delete "):
        task_number = message.content[len("$todo delete "):].strip()
        try:
            index = int(task_number) - 1
        except ValueError:
            await message.channel.send(
                "Please enter a valid task number."
            )
            return

        user_todos = todos.get(user_id, [])

        if index < 0 or index >= len(user_todos):
            await message.channel.send(
                "That task number doesn't exist."
            )
            return

        deleted_task = user_todos.pop(index)
        save_todos(todos)

        await message.channel.send(
            f"Deleted: **{deleted_task['task']}**"
        )


    elif command == "$todo":
        await message.channel.send(
            "**Cuspydo To-Do Commands**\n\n"
            "`$todo add <task>` - Add a task\n"
            "`$todo list` - Show your tasks\n"
            "`$todo done <number>` - Complete a task\n"
            "`$todo delete <number>` - Delete a task"
        )

if __name__ == "__main__":
    token = os.getenv("CUSPYDO_TOKEN")

    if not token:
        print(
            f"token value is {token}. "
            "Did you forget to 'source /path/to/you/.env' or 'vrun'?"
        )
        sys.exit(1)

    client.run(token)