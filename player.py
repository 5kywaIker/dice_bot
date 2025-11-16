user_dict = {
    395938979293167617: "Alice",
    300687482465288194: "Drache",
    517329828727488554: "Nick",
    307989679897051136: "Eric",
    513821779429687296: "Camo",
    509801411119153153: "Jacky",
    383707465411198976: "Leon"
    }

player_attribute_dict = {}
attribute_list = [] #?
attribute_list_normal = [] #easy
attribute_list_saves = [] #easy
attribute_list_attribute = [] #enthält normal & saves in der Reihenfolge in der sie in player_attribute.txt stehen
attribute_list_custom = [] #enthält alle custom attribute von allen spielern zusammengefasst
attribute_list_spells = []
attribute_dict = {} #enthält als Key aus welcher Datei das Attribut kommt, und als Value die Liste der Attribute aus der Datei

# on Bot start, lade alle Spieler-Werte aus der Text Datei in die Player Class
def create_player_dict():
    global player_attribute_dict
    global attribute_list
    global attribute_dict
    user_attribute_dict = {}
    attribute_list = []

    for user_id, user_name in user_dict.items():
        user_attribute_dict[user_name] = set_attribute_dict(user_name)
    player_attribute_dict = user_attribute_dict
    attribute_list = attribute_list_normal+attribute_list_saves+attribute_list_custom
    attribute_dict = {"attribute": attribute_list_attribute, "custom": attribute_list_custom, "spells": attribute_list_spells}

    return (user_attribute_dict)


def set_attribute_dict(user_name):
    global attribute_list_normal
    global attribute_list_saves
    global attribute_list
    global attribute_list_custom

    with open('player_attribute.txt', 'r', encoding='utf-8') as file:
        global attribute_list_attribute
        content = file.readlines()
        attribute_list_temp = content[0].replace("\n", "").split(";")
        attribute_list_attribute = attribute_list_temp[1:]
        temp_attribute_dict = {}

        #loope durch die File, erstelle dict aus attribut : spieler_stat, wenn playername = content[i][0]
        # loope dann über content um zu erstellen
        for line in content:
            player_attribute_list = line.replace("\n", "").split(";")

            if player_attribute_list[0] == user_name:
                for i in range(1, len(player_attribute_list)):
                    temp_attribute_dict[attribute_list_temp[i]] = player_attribute_list[i]
        attribute_list_normal = [text for text in attribute_list_temp if not "save" in text]
        attribute_list_saves = [text for text in attribute_list_temp if "save" in text]

    with open('player_custom.txt', 'r', encoding='utf-8') as file:
        content = file.readlines()

        for i in range(len(content)):
            line = content[i]
            player_attribute_list = line.replace("\n", "").split(";")

            if player_attribute_list[0] == user_name:
                attribute_list_temp = content[i-1].replace("\n", "").split(";")
                for i in range(1, len(player_attribute_list)):
                    temp_attribute_dict[attribute_list_temp[i]] = player_attribute_list[i]
                    if not attribute_list_temp[i] in attribute_list_custom:
                        attribute_list_custom.append(attribute_list_temp[i])

    return(temp_attribute_dict)

