# WoW Guild Crafting Bot

This is a small Discord bot for tracking guild crafting characters.

## Current commands

Use:

```text
/addcraft
/additem
/listitems
/removeitem
/listcraft
/removecraft
```

Example:

```text
/addcraft character_name:Thrall profession:Blacksmithing
/additem character_name:Thrall profession:Blacksmithing item_name:Everforged Longsword
/listitems character_name:Thrall profession:Blacksmithing
/removeitem character_name:Thrall profession:Blacksmithing item_name:Everforged Longsword
/listcraft
/listcraft character_name:Thrall
/removecraft character_name:Thrall
```

The bot stores:

- Discord user
- Character name
- Profession
- Craftable items

The data is saved in `crafting_data.json`.

## Setup

1. Python 3.12 is installed on this machine.
2. Create or reuse the virtual environment:

```powershell
python -m venv .venv
```

3. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Set your Discord bot token:

```powershell
$env:DISCORD_TOKEN="your-bot-token-here"
```

6. Set your Discord server ID for faster slash-command updates while testing:

```powershell
$env:DISCORD_GUILD_ID="your-server-id-here"
```

7. Run the bot:

```powershell
python bot.py
```

If `python` still opens the Microsoft Store in an older terminal window, close that terminal and open a new one before running the commands above.

## Discord setup reminder

This bot now uses a slash command, so you do not need the **Message Content Intent** for `/addcraft`.

After inviting the bot to your server and starting it, Discord may take a short time to show the slash command the first time it syncs.

If you set `DISCORD_GUILD_ID`, the bot will sync commands directly to that server, which is much faster for testing.

## CasaOS

This bot can run on CasaOS as a Docker app.

Files included for that:

- `Dockerfile`
- `docker-compose.yml`

### Before you deploy

Edit `docker-compose.yml` and set:

```yaml
DISCORD_TOKEN: your-bot-token-here
DISCORD_GUILD_ID: your-server-id-here
```

### CasaOS deployment

1. Copy this project folder to your CasaOS machine.
2. In CasaOS, open the terminal or file manager and go to the project folder.
3. Use the custom compose/app option in CasaOS and load `docker-compose.yml`.
4. Start the app.

The bot data will be stored in the `data` folder next to the compose file, so your `crafting_data.json` survives container restarts.
