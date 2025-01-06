# A powerful discord bot.

import discord
import os
import sys


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


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("$prime"):
        prime_str = message.content[7:]
        try:
            prime_int = int(prime_str)
            result = isPrime(prime_int)
            await message.channel.send(result)
        except ValueError:
            await message.channel.send(
                f'Sorry "{prime_str}" is not a valid number. Try again.'
            )


token = os.getenv("CUSPYDO_TOKEN")
if not token:
    print(
        f"token value is {token}. Did you forget to 'source /path/to/you/.env' or 'vrun'?"
    )
    sys.exit(1)
client.run(token)
