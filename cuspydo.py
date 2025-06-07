# A task manager discord bot under construction.

import discord
import os
import sys


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


if __name__ == "__main__":
    token = os.getenv("CUSPYDO_TOKEN")
    if not token:
        print(
            f"token value is {token}. Did you forget to 'source /path/to/you/.env' or 'vrun'?"
        )
        sys.exit(1)
    client.run(token)
    credits
