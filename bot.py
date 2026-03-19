import json
import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


DATA_FILE = Path(os.getenv("CRAFTING_DATA_FILE", "crafting_data.json"))


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"crafters": []}

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def normalize_crafter(entry: dict) -> dict:
    normalized_entry = dict(entry)
    normalized_entry.setdefault("items", [])
    return normalized_entry


def find_crafter(crafters: list[dict], character_name: str) -> dict | None:
    for entry in crafters:
        if entry["character_name"].casefold() == character_name.casefold():
            return entry
    return None


def find_crafters(crafters: list[dict], character_name: str) -> list[dict]:
    return [
        entry
        for entry in crafters
        if entry["character_name"].casefold() == character_name.casefold()
    ]


intents = discord.Intents.default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


@bot.event
async def setup_hook() -> None:
    guild_id = os.getenv("DISCORD_GUILD_ID")
    if guild_id:
        guild = discord.Object(id=int(guild_id))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"Synced commands to guild {guild_id}")
    else:
        await bot.tree.sync()
        print("Synced global commands")


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="addcraft", description="Add a character and crafting profession.")
@app_commands.describe(
    character_name="Your WoW character name",
    profession="The crafting profession for that character",
)
async def addcraft(
    interaction: discord.Interaction, character_name: str, profession: str
) -> None:
    data = load_data()
    crafters = [normalize_crafter(entry) for entry in data.get("crafters", [])]

    existing_entry = find_crafter(crafters, character_name)
    if existing_entry and existing_entry["profession"].casefold() == profession.casefold():
        await interaction.response.send_message(
            f"`{character_name}` already has profession `{profession}` saved."
        )
        return

    entry = {
        "discord_user": str(interaction.user),
        "discord_user_id": interaction.user.id,
        "character_name": character_name,
        "profession": profession,
        "items": [],
    }

    crafters.append(entry)
    data["crafters"] = crafters
    save_data(data)

    await interaction.response.send_message(
        f"Added `{character_name}` with profession `{profession}` for {interaction.user.mention}."
    )


@bot.tree.command(name="listcraft", description="List all saved crafting characters.")
@app_commands.describe(character_name="Optional: show only one character's craftable items")
async def listcraft(
    interaction: discord.Interaction, character_name: str | None = None
) -> None:
    data = load_data()
    crafters = [normalize_crafter(entry) for entry in data.get("crafters", [])]

    if not crafters:
        await interaction.response.send_message(
            "**Saved crafting characters**\n```text\ncharactername | profession | items\n```"
        )
        return

    if character_name:
        matching_crafters = find_crafters(crafters, character_name)
        if not matching_crafters:
            await interaction.response.send_message(
                f"No crafting entry found for `{character_name}`."
            )
            return

        lines = []
        for crafter in matching_crafters:
            items = crafter.get("items", [])
            item_text = ", ".join(items) if items else "No items added yet"
            lines.append(
                f"{crafter['character_name']} | {crafter['profession']} | {item_text}"
            )

        table = "charactername | profession | items\n" + "\n".join(lines)
        message = f"**Crafting details for {character_name}**\n```text\n{table}\n```"
        await interaction.response.send_message(message)
        return

    lines = [
        f"{entry['character_name']} | {entry['profession']} | {len(entry.get('items', []))} item(s)"
        for entry in crafters
    ]

    table = "charactername | profession | items\n" + "\n".join(lines)
    message = f"**Saved crafting characters**\n```text\n{table}\n```"
    await interaction.response.send_message(message)


@bot.tree.command(
    name="listitems",
    description="List all craftable items for a character and profession.",
)
@app_commands.describe(
    character_name="The WoW character name",
    profession="The profession to view items for",
)
async def listitems(
    interaction: discord.Interaction, character_name: str, profession: str
) -> None:
    data = load_data()
    crafters = [normalize_crafter(entry) for entry in data.get("crafters", [])]

    crafter = next(
        (
            entry
            for entry in crafters
            if entry["character_name"].casefold() == character_name.casefold()
            and entry["profession"].casefold() == profession.casefold()
        ),
        None,
    )
    if not crafter:
        await interaction.response.send_message(
            f"No crafting entry found for `{character_name}` with profession `{profession}`."
        )
        return

    items = crafter.get("items", [])
    item_lines = items if items else ["No items added yet"]
    table = (
        "charactername | profession | items\n"
        f"{crafter['character_name']} | {crafter['profession']} | {', '.join(item_lines)}"
    )
    await interaction.response.send_message(
        f"**Craftable items**\n```text\n{table}\n```"
    )


@bot.tree.command(name="additem", description="Add a craftable item to a character profession.")
@app_commands.describe(
    character_name="The WoW character name",
    profession="The profession to add the item under",
    item_name="An item this character can craft",
)
async def additem(
    interaction: discord.Interaction, character_name: str, profession: str, item_name: str
) -> None:
    data = load_data()
    crafters = [normalize_crafter(entry) for entry in data.get("crafters", [])]

    crafter = next(
        (
            entry
            for entry in crafters
            if entry["character_name"].casefold() == character_name.casefold()
            and entry["profession"].casefold() == profession.casefold()
        ),
        None,
    )
    if not crafter:
        await interaction.response.send_message(
            f"No crafting entry found for `{character_name}` with profession `{profession}`. "
            "Add it first with `/addcraft`."
        )
        return

    items = crafter.setdefault("items", [])
    if any(existing_item.casefold() == item_name.casefold() for existing_item in items):
        await interaction.response.send_message(
            f"`{character_name}` already has `{item_name}` in their item list."
        )
        return

    items.append(item_name)
    data["crafters"] = crafters
    save_data(data)

    await interaction.response.send_message(
        f"Added item `{item_name}` to `{character_name}` under `{profession}`."
    )


@bot.tree.command(
    name="removeitem", description="Remove a craftable item from a character profession."
)
@app_commands.describe(
    character_name="The WoW character name",
    profession="The profession to remove the item from",
    item_name="The item to remove",
)
async def removeitem(
    interaction: discord.Interaction, character_name: str, profession: str, item_name: str
) -> None:
    data = load_data()
    crafters = [normalize_crafter(entry) for entry in data.get("crafters", [])]

    crafter = next(
        (
            entry
            for entry in crafters
            if entry["character_name"].casefold() == character_name.casefold()
            and entry["profession"].casefold() == profession.casefold()
        ),
        None,
    )
    if not crafter:
        await interaction.response.send_message(
            f"No crafting entry found for `{character_name}` with profession `{profession}`."
        )
        return

    items = crafter.get("items", [])
    item_to_remove = next(
        (existing_item for existing_item in items if existing_item.casefold() == item_name.casefold()),
        None,
    )
    if not item_to_remove:
        await interaction.response.send_message(
            f"`{item_name}` was not found for `{character_name}` under `{profession}`."
        )
        return

    items.remove(item_to_remove)
    data["crafters"] = crafters
    save_data(data)

    await interaction.response.send_message(
        f"Removed item `{item_to_remove}` from `{character_name}` under `{profession}`."
    )


@bot.tree.command(name="removecraft", description="Remove saved crafting entries by character name.")
@app_commands.describe(character_name="The WoW character name to remove")
async def removecraft(interaction: discord.Interaction, character_name: str) -> None:
    data = load_data()
    crafters = [normalize_crafter(entry) for entry in data.get("crafters", [])]

    remaining_crafters = [
        entry
        for entry in crafters
        if entry["character_name"].casefold() != character_name.casefold()
    ]

    removed_count = len(crafters) - len(remaining_crafters)
    if removed_count == 0:
        await interaction.response.send_message(
            f"No crafting entries found for `{character_name}`."
        )
        return

    data["crafters"] = remaining_crafters
    save_data(data)

    await interaction.response.send_message(
        f"Removed {removed_count} crafting entr"
        f"{'y' if removed_count == 1 else 'ies'} for `{character_name}`."
    )


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Set the DISCORD_TOKEN environment variable before starting the bot.")

    bot.run(token)


if __name__ == "__main__":
    main()
