import sys
import re
import player
import CustomErrors
import dice_roller


#TODO: am Ende per for schleife über isolated_command_list iterieren.
# Falls sie mehr als 2 Elemente enthält, ist ein weiterer command in position [2] und [3] und der Prefix aus prefix_modifier_list[1] muss ausgelesen werden.
# Aktuelle keine Handhabe der additional_modifier_list. Diese sollte nur zum aller letzten command addiert werden, da es nur die modifier hinter der letzten "]" sind.
#TODO: Behandlung von ad[di[mod]] = r[mod] und ad[ad[mod]] = ad[mod] einbauen.
async def call_custom_command(ctx, player_id, custom_command):
    current_module = sys.modules["bot_commands"]
    custom_command_list = await split_dice_string(custom_command)       #zählt die Anzahl an öffnenden und schließenden Brackets. Wird genutzt, um Brackets in Brackets zu ignorieren.
    counter = 0     #trackt was sich innerhalb und was außerhalb von Klammern befindet,
                    # indem er sich den Index der intial öffnenden Klammer (für innerhalb) oder der final schließenden Klammer (für außerhalb)  merkt.
    relevant_bracket_index = 0
    isolated_command_list = []      # enthält den Befehl vor den Klammern, gefolgt vom Inhalt der Klammern als nächstes Listenelement. Wenn len > 2, dann enthielt der custom_command mehrere Befehle.
    additional_modifier_list = custom_command_list.copy()       #enthält modifier die sich außerhalb der Klammern befinden, aber nur solche hinter der Klammer.
    prefix_modifier_list = []       # Liste mit Listen welche alle Modifier vor einer initial öffnenden Klammer enthälen. Bei Eingabe 2+ad[2]+4+ad[4]+5 enthält prefix_modifier_list [['2','+']['+','4','+']]

    for i in range(len(custom_command_list)):
        to_roll = custom_command_list[i]
        if to_roll == "[":
            if counter == 0:
                command = custom_command_list[i-1]
                isolated_command_list.append(command)
                if i > 1:
                    prefix_modifier_list.append(custom_command_list[relevant_bracket_index:i-1])
                    for to_replace in range(relevant_bracket_index, i-1):
                        additional_modifier_list[to_replace] = ""
                relevant_bracket_index = i+1
            counter +=1
        elif to_roll == "]":
            counter -= 1
            if counter == 0:
                command = ""
                for j in range(relevant_bracket_index, i):
                    command += custom_command_list[j]
                #den command, die eckigen klammern und alles dazwischen aus der additional_modifier_list löschen.
                for to_replace in range(relevant_bracket_index-2, i+1):
                    additional_modifier_list[to_replace] = ""
                isolated_command_list.append(command)
                relevant_bracket_index = i + 1

    #überprüft ob r[], ad[] oder di[] aufgerufen wird. Ansonsten nicht 1d20 hinzufügen
    if len(isolated_command_list[0]) < 3:
        # wenn in den Eckigen Klammern kein Würfel steht, füge 1d20 hinzu
        if not re.search(r"^[1-9][a-zA-Z][1-9]", isolated_command_list[1]):
            isolated_command_list[1] = "1d20+" + isolated_command_list[1]

    single_string = ""
    prefix_string = ""
    for single in additional_modifier_list:
        single_string += single
    try:
        for prefix in prefix_modifier_list[0]:
            prefix_string += prefix
    except IndexError:
        pass

    isolated_command_list[1] = str(prefix_string)+str(isolated_command_list[1])+str(single_string)

    #den input für den command (steht an Stelle 1) an den Kommas trennen und als Liste zurück schreiben.
    if not isolated_command_list[0] == "print":
        isolated_command_list[1] = isolated_command_list[1].split(",")
    else:
        isolated_command_list[1] = [isolated_command_list[1]]

    custom_command = isolated_command_list[0] + "_command"

    await getattr(current_module, custom_command)(ctx, player_id, *isolated_command_list[1])

    #not sure ob das hier ausgeführt werden sollte.
    #falls es irgendwann zu problemen kommt, wo ad[] oder di[] nicht richtig ausgeführt wird, wenn mehrere Befehle hintereinander stehen, könnte das hier der Auslöser sein.
    dice_roller.adv_modifier = 0
    dice_roller.adv_modifier_attribute = 0
    return

async def replace_attribute(ctx, player_id, to_roll):
    """
    checkt vorm würfeln ob einer der eingabewerte ein attribut ist und ersetze das Attribut durch den modifier-wert.
    """
    temp_to_roll = await split_dice_string(to_roll)
    temp_player_name = player.user_dict[player_id]
    attribute_dict = player.player_attribute_dict.get(temp_player_name)
    original_input_modified = ""
    to_roll = ""

    for i in range(len(temp_to_roll)):
        temp_einzel_eingabe = temp_to_roll[i]

        #wenn kein Buchstabe in der Eingabe ist, überspringe die Überprüfung match_substring und nehme das nächste Element.
        # Spart Zeit, weil ansonsten jedes Element in  attribute_list mit temp_einzel_eingabe verglichen werden müsste
        if not re.search(r"^[a-zA-Z][a-zA-Z]", temp_einzel_eingabe):
            original_input_modified += temp_einzel_eingabe
            continue

        custom_attribute_list = await match_substring(player.attribute_list, temp_einzel_eingabe)
        if len(custom_attribute_list) > 0:

            custom_modifier = str(attribute_dict[custom_attribute_list[0]])
            custom_modifier_list = await split_dice_string(custom_modifier)
            custom_modifier = ""
            temp_custom_modifier_list = custom_modifier_list

            if "[" not in custom_modifier_list:

                #was moved inside the if check, to prevent Spaces getting deleted out of print[Hello World] Eingaben.
                while " " in custom_modifier_list:
                    custom_modifier_list.remove(" ")

                for custom in range(len(temp_custom_modifier_list)):
                    nested_modifier = temp_custom_modifier_list[custom]

                    #spare match_substring Aufrufe
                    if not re.search(r"[a-zA-Z]", nested_modifier):
                        continue

                    nested_command_list = await match_substring(player.attribute_list, nested_modifier)

                    if len(nested_command_list) > 0:
                        custom_modifier_list[custom], input_modified = await replace_attribute(ctx, player_id, nested_command_list[0])

            for custom in range(len(custom_modifier_list)):
                custom_modifier += custom_modifier_list[custom]
            temp_to_roll[i] = custom_modifier

            if "save" in custom_attribute_list[0]:
                temp_einzel_eingabe = str(custom_attribute_list[0][:4]) + "sv"
            else:
                temp_einzel_eingabe = custom_attribute_list[0][:4]

        original_input_modified += temp_einzel_eingabe

    for i in temp_to_roll:
        to_roll += i

    return (to_roll, original_input_modified)


async def split_dice_string(string_w) -> list:
    """
    splittet den string an allen charakteren die nicht Buchstabe oder Zahl sind
    """
    split_string_list = re.split(r'(\W)', string_w)
    while "" in split_string_list:
        split_string_list.remove("")
    return (split_string_list)


# todo Füge überprüfung ob len(matching_list) >1, == 1 oder 0 ein.
# werfe error auf >1, return andernfalls
# todo: füge überprüfung ein, ob saving throw oder nicht, indem to_roll auf sv überprüft wird, maybe return in welcher liste der wert gefunden wurde (normal, save, custom, spell)
async def match_substring(list_to_search, search_string):
    """
    Looks through a list of strings and returns all strings that start with "search_string" as a sub_string
    """
    if search_string.endswith("save") or search_string.endswith("sv"):
        search_string = re.sub(r"(save|sv).*", "", search_string)
        list_to_search = player.attribute_list_saves

    matching_list = [text for text in list_to_search if text.startswith(search_string)]

    return (matching_list)
