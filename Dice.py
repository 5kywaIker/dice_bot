import os
from dice_bot import bot
from dotenv import load_dotenv
import bot_functions

load_dotenv()

if __name__ == "__main__":

    token = os.getenv('TOKEN')
    bot_functions.create_player_dict()
    bot.run(token)  # Letzte Zeile$