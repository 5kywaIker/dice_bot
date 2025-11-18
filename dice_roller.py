import re
import random
import player
import CustomErrors
import bot_functions

#adv_modifier: 0[normal], 1[advantage], 2[disadvantage]
adv_modifier = 0
adv_modifier_attribute = 0

async def roll_standard(ctx, to_roll, player_id):
    roll_result_eval_string = ""  # zum tracken und späteren addieren der Würfelergebnisse
    roll_result_output_string = ""  # zum tracken und späteren printen der Würfelergebnisse
    last_roll_was_dice = False  # für die Formatierung der Ausgabe
    original_input_modified = ""

    # Teile den Input Befehl in ein Array auf mit selbstgebauter funktion weiter unten
    # aus '1d20+1d10+7' wird ['1d20', '+', '1d10', '+', '7']
    to_roll_list = await bot_functions.split_dice_string(to_roll)

    # gehe das Array durch, wenn ein Eintrag "d" enthält, würfele den entsprechenden Würfel
    # tracke die Ergebnisse in zwei verschiedenen Strings, eval & output
    for dice in to_roll_list:

        if re.search(r"^[a-zA-Z][a-zA-Z]", dice):  # überprüfen, ob attribut übergeben wurde
            dice_output, dice_eval, dice = await roll_attribute(ctx, dice, player_id)
        elif "d" in dice:  # überprüfen ob d20 übergeben wurde
            dice_output, dice_eval = await roll_dice(dice)
            if not last_roll_was_dice:  # Formatierung von []
                roll_result_output_string += " ["
                last_roll_was_dice = True
            else:
                roll_result_output_string += ", "
        else:  # sonst einfach die Übergabe zurück geben
            if last_roll_was_dice:
                roll_result_output_string += "] "
                last_roll_was_dice = False
            else:
                roll_result_output_string += " "
            dice_output = dice
            dice_eval = dice
        roll_result_output_string += str(dice_output)
        roll_result_eval_string += str(dice_eval)

        original_input_modified += str(dice) + " "

    if last_roll_was_dice:
        roll_result_output_string += "]"
    roll_result_eval = eval(roll_result_eval_string)

    return (roll_result_output_string, str(roll_result_eval), original_input_modified)


# würfele "1d20" Würfel o.ä. - Eingabe als String mit dem Würfel ohne Modifier. Ohne Eingabe Würfele einen d20
async def roll_dice(to_roll="1d20"):
    to_roll_list = re.split(r'd', to_roll)
    number_of_dice = int(to_roll_list[0])
    dice_size = int(to_roll_list[1])
    roll_result_output = ""
    roll_result_eval = 0
    global adv_modifier

    if not adv_modifier == 0:

        if adv_modifier == 1:
            for i in range(0, number_of_dice):

                rolled_number1 = random.randint(1, dice_size)
                rolled_number2 = random.randint(1, dice_size)
                rolled_number = max(rolled_number1, rolled_number2)
                if 0 < i < number_of_dice:
                    roll_result_output += "]" " + " "["
                roll_result_output += str(rolled_number1) + ", " + str(rolled_number2)
                roll_result_eval += rolled_number

        if adv_modifier == 2:
            for i in range(0, number_of_dice):

                rolled_number1 = random.randint(1, dice_size)
                rolled_number2 = random.randint(1, dice_size)
                rolled_number = min(rolled_number1, rolled_number2)
                if 0 < i < number_of_dice:
                    roll_result_output += "]" " + " "["
                roll_result_output += str(rolled_number1) + ", " + str(rolled_number2)
                roll_result_eval += rolled_number

    else:
        for i in range(0, number_of_dice):

            rolled_number = random.randint(1, dice_size)
            if 0 < i < number_of_dice:
                roll_result_output += ", "
            roll_result_output += str(rolled_number)
            roll_result_eval += rolled_number

    adv_modifier = 0
    return (roll_result_output, str(roll_result_eval))


async def roll_attribute(ctx, to_roll, player_id):
    '''
    bekommt den Namen eines Attributs in to_roll übergeben, guckt den Attr Wert des Spielers nach und würfelt einen d20 mit dem Ergebnis
    :param ctx:Context
    :param to_roll:str
    :param player_id:str
    :return:(str,str,str)
    '''
    global adv_modifier
    global adv_modifier_attribute
    adv_modifier = adv_modifier_attribute

    player_name = player.user_dict[player_id]

    if "sav" in to_roll or "sv" in to_roll:  # überprüfen ob das Attr ein Modifier ist
        to_roll = re.sub(r"(sav|sv).*", "", to_roll)
        to_roll = await bot_functions.match_substring(player.attribute_list_saves, to_roll)
    else:
        to_roll = await bot_functions.match_substring(player.attribute_list_normal, to_roll)

    if len(to_roll) == 0:
        raise CustomErrors.NotExistingMatching
    if len(to_roll) > 1:
        raise CustomErrors.NotUniqueMatching  # custom Error

    to_roll = to_roll[0]

    # Mit dem Spielernamen wird das Dict des Spielers abgerufen
    # daraus wird der Wert des angefragten Attributs in to_roll_attribute_modifier geschrieben
    to_roll_attribute_modifier = str(player.player_attribute_dict.get(player_name)[to_roll])

    if "[" in to_roll_attribute_modifier:
        await bot_functions.call_custom_command(ctx, to_roll_attribute_modifier, player_id)

    # original_input auf attribute_namen_kurz setzen, wenn standard attribut gewürfelt wurde
    if "save" in to_roll:
        original_input_modified = str(to_roll[:4]) + "sv"
    else:
        original_input_modified = to_roll[:4]

    # guckt ob der Modifier 1d20 o.ä. enthält. Wenn ja, roll_standard erneute aufrufen mit dem modifier als to_roll übergabe. Dies würfelt den Modifier vollständig aus und arbeitet ihn ab.
    # wenn der Modifier keinen d20 enthält, dann wird im else: ein d20 hinzugefügt
    if "d" in to_roll_attribute_modifier:
        roll_result_output, roll_result_eval, original_input_modified = await roll_standard(ctx, str(to_roll_attribute_modifier), player_id)
    else:
        to_roll_attribute_modifier = int(to_roll_attribute_modifier)  # remove extra leerzeichen, oder mathematische operanten
        roll_result_output, roll_result_eval = await roll_dice()

        roll_result_eval += "+" + str(to_roll_attribute_modifier)
        roll_result_output = " [" + roll_result_output + "]" + " + " + str(to_roll_attribute_modifier)

    adv_modifier = 0

    return (roll_result_output, str(roll_result_eval), str(original_input_modified))