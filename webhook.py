from discord import SyncWebhook 
from discord import Embed
from discord import Colour
from discord import File
import aiohttp
from datetime import datetime
from bottoken import BOT_TOKEN

class DiscordBot:
    def __init__(self):
        self.webhook = SyncWebhook.from_url(BOT_TOKEN)

        return None
    
    """
    Takes 4 arguments:
        1. Screenshot, path to local file.
        2. Count, count of soft resets.
        3. Pokemon, name of pokemon.
        4. Time elapsed, total time the hunt took (while resetting).
    """
    def _send_message(self, args: list) -> None:
        if len(args) != 4:
            print(f"Arguments passed to _send_message incorrect. 4 expected, {len(args)} given.")
            return None

        screenshot = File(args[0], "screenshot.png")
        count = args[1]
        pokemon = args[2].capitalize()
        time_elapsed = args[3]

        embed = Embed()
        embed.title = "Shiny! ✨"
        embed.colour = Colour.random()
        embed.description = f"""
                            {pokemon} was found at {count} encounters!
                            Time elapsed: ~{time_elapsed}.
                            """
        embed.timestamp = datetime.now()
        embed.set_image(url=f"attachment://screenshot.png")

        self.webhook.send(file=screenshot, embed=embed)
        print("Shiny message sent!")
