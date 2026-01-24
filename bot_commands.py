import sys
import re
from os import write
import player
import CustomErrors
import dice_roller
import bot_functions

original_input_global = ""

#Standard Funktion zum Würfeln. Handled die Logik fürs Würfeln und die Formatierung der Ausgabe.
async def r_command(ctx, player_id, to_roll, temp_adv_modifier=0):

    dice_roller.adv_modifier = temp_adv_modifier
    dice_roller.adv_modifier_attribute = temp_adv_modifier
    original_input_modified = to_roll
    global original_input_global
    original_input_modified = to_roll

    #ersetzt alle attributnamen in to_roll mit dem dazugehörigen Modifier.
    #Wird nur ausgeführt, wenn der input kein nested command ist, ansonsten würde change[str 6] nicht funktionieren, da er str durch den modifier ersetzt
    if "[" not in to_roll:
        to_roll, original_input_modified = await bot_functions.replace_attribute(ctx, player_id, to_roll)        #original_input wird später überschrieben. Muss noch behandelt werden.

    if len(original_input_global) == 0:
        original_input_global = original_input_modified
        original_input_global = original_input_global.split("|")

    #mehrfach_würfeln, und die ergebnisse seperat zurückgeben, falls anzeigender seperator im string "to_roll" ("|" oder " ")
    to_roll = re.split(r"(\|)", to_roll)
    temp_to_roll = []
    bracket_count = 0
    offset = 0
    for i in range(len(to_roll)):
        search_opening = to_roll[i]
        if "[" in search_opening:
            if bracket_count == 0:
                opening_index = i
            bracket_count += search_opening.count("[") - search_opening.count("]")
            if bracket_count == 0:
                search_opening = ""
                closing_index = i
                del temp_to_roll[opening_index-offset:]
                for in_brackets in to_roll[opening_index:closing_index+1]:
                    search_opening += in_brackets
                offset = opening_index-closing_index
        elif "]" in search_opening:
            bracket_count += search_opening.count("[") - search_opening.count("]")
            if bracket_count == 0:
                search_opening = ""
                closing_index = i
                del temp_to_roll[opening_index - offset:]
                for in_brackets in to_roll[opening_index:closing_index + 1]:
                    search_opening += in_brackets
                offset += opening_index - closing_index
        #wenn "|" außerhalb der Klammern steht, dann nicht wieder zu to_roll hinzufügen.
        elif search_opening == "|" and bracket_count == 0:
            continue
        temp_to_roll.append(search_opening)
    to_roll = temp_to_roll


    for i in range(len(to_roll)):
        dice=to_roll[i]
        try:
            original_input_modified = original_input_global[0]
        except IndexError:
            pass

        # auf nested commands prüfen, falls nested command, dann den entsprechend command aufrufen. Nach dem command wird das printen übersprungen und zum nächsten Element von to_roll gegangen.
        # TODO: aktuell wird nur die erste eckige Klammer ausgeführt. Füge in call_custom_command behandlung von mehreren eckigen klammern ein.
        if "[" in dice:
            await bot_functions.call_custom_command(ctx, player_id, dice)
            continue

        # überprüfe ob to_roll nur modifier enthält, wenn ja, dann erweitere to_roll um 1d20 am anfang. Für custom commands die keinen d20 enthalten und "-r dext|+1 oder so
        if not re.search(r"[a-zA-Z]", dice):
            dice = "1d20" + "+" + str(dice)

        roll_result_output_string, roll_result_eval, original_input = await dice_roller.roll_standard(ctx, dice, player_id)
        output_message = str(original_input_modified) + " :" + str(roll_result_output_string) + " = " + str(roll_result_eval)
        await ctx.reply(output_message)
        try:
            original_input_global.pop(0)
        except IndexError:
            pass

    dice_roller.adv_modifier = 0
    dice_roller.adv_modifier_attribute = 0


async def ad_command(ctx, player_id, to_roll, temp_adv_modifier=1):
    await r_command(ctx, player_id, to_roll, temp_adv_modifier)

async def di_command(ctx, player_id, to_roll, temp_adv_modifier=2):
    await r_command(ctx, player_id, to_roll, temp_adv_modifier)

async def spell_command(ctx, player_id, to_cast, bonus_damage, spell_level, upcast_level="0"):
    #führt automatisch den vom Spieler eingespeicherten Spell aus und zieht dann den entsprechenden Spellslot ab
    spell_level = int(spell_level)
    upcast_level_list = upcast_level.split("|")
    if "" in upcast_level_list:
        upcast_level_list.remove("")
        upcast_level = upcast_level_list[0]
    else:
        upcast_level = upcast_level_list[0]
    spell_modifier_list = to_cast.split(",")
    upcast_level = max(spell_level, int(upcast_level))
    bonus_damage = str(bonus_damage) * (upcast_level- spell_level)
    to_cast = str(to_cast) + bonus_damage

    await r_command(ctx, player_id, to_cast, dice_roller.adv_modifier)

    if spell_level > 0:
        ssc = await show_command(ctx, player_id, "spell_slots_current")
        ssc = re.split(r"\W", ssc)
        while "" in ssc:
            ssc.remove("")
        if int(ssc[spell_level-1]) < 1:
            raise CustomErrors.SpecificError(f'Du hast nicht genug Spell Slots um diesen Spell auf Level {spell_level} zu casten')
        ssc[spell_level-1] = str(int(ssc[spell_level-1]) - 1)
        new_spell_slots = "[" + str(ssc[0])
        if len(ssc) > 1:
            for slot in ssc[1:]:
                new_spell_slots += "," + str(slot)
        new_spell_slots += "]"
        await change_command(ctx, player_id, "spell_slots_current", new_spell_slots)

    return

#maybe auch im schreibcommand einfach nochmal über play_custom.txt loopen, bis line.replace("\n", "").split(";")[0] == player_name,
#und dann line.replace("\n", "").split(";")[content(content.index(line)-1).replace("\n", "").split(";").index(to_change)] = to_change
async def change_command(ctx, player_id, request, change_to):
    request_type = ""               #art des request commands, ob attribute, custom oder spell
    request_index = 0               #index in der attribute liste des spielers, in welchem der requested command steht (in player_type.txt
    att_modifier_list = []          #liste mit allen modifiern des spielers aus der jeweiligen player_type.txt
    request_long_list = await bot_functions.match_substring(player.attribute_list, request)

    ### todo: in match_string einbinden!
    if len(request_long_list) == 0:
        raise CustomErrors.NotExistingMatching(request)
    ###

    request_long = request_long_list[0]

    #gibt zurück ob das attribut in attribute, custom oder spells ist
    for k, v in player.attribute_dict.items():
        if request_long in v:
            request_type = k
            break

    if request_type == "":
        raise CustomErrors.NotExistingMatching(request_long)

    file_name_string = f'player_{request_type}.txt'
    user_name = player.user_dict[player_id]
    att_dict = player.player_attribute_dict[user_name]

    att_name_list = list(att_dict)                          #gibt alle keys aus dem attribute dict des spielers, der den Command aufgerufen hat
    player_number = list(player.player_attribute_dict)
    player_number = player_number.index(user_name)

    #hole request_index und att_modifier_list aus player_tyoe.txt

    player_number = player_number * 2
    with open(file_name_string) as file:
        lines = file.readlines()
        if (player_number <= len(lines)):
            att_modifier_list = lines[player_number].replace("\n", "").split(";")
            for i in range(len(att_modifier_list)):
                if att_modifier_list[i] == request_long:
                    request_index = i
                    att_modifier_list = lines[player_number+1].replace("\n", "").split(";")
                    break
    player_number = player_number + 1                       #setze player_number auf die zeile der textdatei in welcher die Modifier des Spielers stehen


    old_value = att_modifier_list[request_index]
    att_modifier_list[request_index] = change_to
    write_string = str(user_name)

    #schreibe in write string die attribute
    for i in att_modifier_list[1:]:
        write_string += ";" + i


    with open(file_name_string) as file:
        lines = file.readlines()
        if (player_number <= len(lines)):
            lines[player_number] = write_string + "\n"
            with open(file_name_string, "w") as file:
                for line in lines:
                    file.write(line)

    player.create_player_dict()
    await ctx.reply(f"Dein {request_long} Eintrag wurde von {old_value} zu {change_to} geändert")
    return(request_long, old_value)


async def delete_command(ctx, player_id, request):
    request_type = ""               #art des request commands, ob attribute, custom oder spell
    request_index = 0               #index in der attribute liste des spielers, in welchem der requested command steht (in player_type.txt
    att_name_list = []              # liste mit allen attr namen des spielers aus der jeweiligen player_type.txt
    att_modifier_list = []          #liste mit allen modifiern des spielers aus der jeweiligen player_type.txt
    request_long_list = await bot_functions.match_substring(player.attribute_list, request)

    ### todo: in match_string einbinden!
    if len(request_long_list) == 0:
        raise CustomErrors.NotExistingMatching(request)
    ###

    request_long = request_long_list[0]

    #gibt zurück ob das attribut in attribute, custom oder spells ist
    for k, v in player.attribute_dict.items():
        if request_long in v:
            request_type = k
            break

    if request_type == "":
        raise CustomErrors.NotExistingMatching(request_long)

    if request_type == "attribute":
        raise CustomErrors.SpecificError(f'Das Attribut "{request_long}" kann nicht gelöscht werden. Das brauchst du noch. Du kannst allerdings mit /change den modifier ändern.')

    file_name_string = f'player_{request_type}.txt'
    user_name = player.user_dict[player_id]
    att_dict = player.player_attribute_dict[user_name]

    att_name_list = list(att_dict)                          #gibt alle keys aus dem attribute dict des spielers, der den Command aufgerufen hat
    player_number = list(player.player_attribute_dict)
    player_number = player_number.index(user_name)

    #hole request_index und att_modifier_list aus player_type.txt

    player_number = player_number * 2
    with open(file_name_string) as file:
        lines = file.readlines()
        if (player_number <= len(lines)):
            att_name_list = lines[player_number].replace("\n", "").split(";")
            for i in range(len(att_name_list)):
                if att_name_list[i] == request_long:
                    request_index = i
                    att_modifier_list = lines[player_number+1].replace("\n", "").split(";")
                    break
    player_number = player_number + 1                       #setze player_number auf die zeile der textdatei in welcher die Modifier des Spielers stehen

    old_value = att_modifier_list[request_index]
    del att_name_list[request_index]
    del att_modifier_list[request_index]
    write_name_string = str(user_name)
    write_modifier_string = str(user_name)

    #schreibe in write string die attribute
    for i in att_name_list[1:]:
        write_name_string += ";" + str(i)
    for i in att_modifier_list[1:]:
        write_modifier_string += ";" + str(i)

    with open(file_name_string) as file:
        lines = file.readlines()
        if (player_number <= len(lines)):
            lines[player_number-1] = write_name_string + "\n"
            lines[player_number] = write_modifier_string + "\n"
            with open(file_name_string, "w") as file:
                for line in lines:
                    file.write(line)

    player.create_player_dict()

    await ctx.reply(f"Dein {request_long} Eintrag mit dem Inhalt {old_value} wurde gelöscht")
    return(request_long, old_value)

async def new_command(ctx, player_id, command_name, modifier):
    user_name = player.user_dict[player_id]
    player_number = list(player.player_attribute_dict)
    player_number = player_number.index(user_name) * 2
    write_name_string = str(user_name)
    write_modifier_string = str(user_name)

    if command_name in player.player_attribute_dict[user_name]:
        raise CustomErrors.AlreadyExisistingError(command_name)
        #Entkommentieren, wenn intended behaviour bei bereits existierendem command name ist, den commmand zu ändern. Hat probleme, wenn -new für -new_spell benutzt wird
        #await change_command(ctx, command_name, modifier, player_id)
        #raise CustomErrors.CustomCommandEnd

    with open("player_custom.txt") as file:
        lines = file.readlines()
        att_name_list = lines[player_number].replace("\n", "").split(";")
        att_name_list.append(command_name)
        att_modifier_list = lines[player_number+1].replace("\n", "").split(";")
        att_modifier_list.append(modifier)
        for att_name in att_name_list[1:]:
            write_name_string += ";" + str(att_name)
        for att_modifier in att_modifier_list[1:]:
            write_modifier_string += ";" + str(att_modifier)
        if (player_number <= len(lines)):
            lines[player_number] = write_name_string + "\n"
            lines[player_number+1] = write_modifier_string + "\n"
            with open("player_custom.txt", "w") as file:
                for line in lines:
                    file.write(line)

    player.create_player_dict()
    return

async def new_spell_command(ctx, player_id, command_name, modifier, spell_scaling, spell_level):
    user_name = player.user_dict[player_id]
    player_number = list(player.player_attribute_dict)
    player_number = player_number.index(user_name) * 2
    write_name_string = str(user_name)
    write_modifier_string = str(user_name)
    modifier_string = "spell["

    if command_name in player.player_attribute_dict[user_name]:
        raise CustomErrors.AlreadyExisistingError(command_name)

    modifier_string += str(modifier) + "," + str(spell_scaling) + "," + str(spell_level)
    modifier = modifier_string + "]"

    with open("player_spells.txt") as file:
        lines = file.readlines()
        att_name_list = lines[player_number].replace("\n", "").split(";")
        att_name_list.append(command_name)
        att_modifier_list = lines[player_number+1].replace("\n", "").split(";")
        att_modifier_list.append(modifier)
        for att_name in att_name_list[1:]:
            write_name_string += ";" + str(att_name)
        for att_modifier in att_modifier_list[1:]:
            write_modifier_string += ";" + str(att_modifier)
        if (player_number <= len(lines)):
            lines[player_number] = write_name_string + "\n"
            lines[player_number+1] = write_modifier_string + "\n"
            with open("player_spells.txt", "w") as file:
                for line in lines:
                    file.write(line)
    player.create_player_dict()
    return

async def show_command(ctx, player_id, request, *args):

    user_name = player.user_dict[player_id]

    if request in list(player.attribute_dict):
        file_name_string = f'player_{request}.txt'
        player_number = list(player.player_attribute_dict)
        player_number = player_number.index(user_name)
        player_number = player_number * 2
        with open(file_name_string) as file:
            lines = file.readlines()
            att_name_list = lines[player_number].replace("\n", "").split(";")
            return(att_name_list[1:])

    request_long = await bot_functions.match_substring(player.attribute_list, request)
    att_dict = player.player_attribute_dict[user_name]
    return(att_dict[request_long[0]])

async def showall_command(ctx, player_id):
    user_name = player.user_dict[player_id]
    att_dict = player.player_attribute_dict[user_name]
    att_name_list = list(att_dict)
    return(att_dict)

async def print_command(ctx, player_id, output):
    await ctx.reply(str(output))
