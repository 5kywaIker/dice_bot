import os
from dice_bot import bot, create_custom
from dotenv import load_dotenv
import bot_functions
import player

load_dotenv()

if __name__ == "__main__":

    token = os.getenv('TOKEN')
    player.create_player_dict()
    bot.run(token)  # Letzte Zeile$
