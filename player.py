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
attribute_list = {}
attribute_list_normal = []
attribute_list_saves = []
attribute_list_custom = []

# on Bot start, lade alle Spieler-Werte aus der Text Datei in die Player Class
def create_player_dict():
    global player_attribute_dict
    user_attribute_dict = {}

    for user_id, user_name in user_dict.items():
        user_attribute_dict[user_name] = set_attribute_dict(user_name)
    player_attribute_dict = user_attribute_dict
    return (user_attribute_dict)

    
def set_attribute_dict(user_name):
    with open('player_attribute.txt', 'r', encoding='utf-8') as file:
        global attribute_list_normal
        global attribute_list_saves
        global attribute_list
        global attribute_list_custom
        content = file.readlines()
        attribute_list = content[0].replace("\n", "").split(",")
        attribute_dict = {}
    
        #loope durch die File, erstelle dict aus attribut : spieler_stat, wenn playername = content[i][0]
        # loope dann über content um zu erstellen
        for line in content:
            player_attribute_list = line.replace("\n", "").split(",")
            
            if player_attribute_list[0] == user_name:
                for i in range(1, len(player_attribute_list)):
                    attribute_dict[attribute_list[i]] = player_attribute_list[i]
        attribute_list_normal = [text for text in attribute_list[:32] if not "save" in text]
        attribute_list_saves = [text for text in attribute_list[:32] if "save" in text]
        attribute_list_custom = attribute_list[32:]
        return(attribute_dict)

