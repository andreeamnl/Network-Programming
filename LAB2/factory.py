from player import Player
import xml.etree.ElementTree as ET
import player_pb2



class PlayerFactory:
    def to_json(self, players):
        dicts_list = []
        
        for player in players:
            ##print(player.nickname)
            dict={}
            dict["nickname"]=player.nickname
            dict["email"]=(player.email)
            dict["date_of_birth"]=player.date_of_birth.strftime("%Y-%m-%d")
            dict["xp"]=(player.xp)
            dict["class"]=(player.cls)
            dicts_list.append(dict)
        ##print("debug 1")
        ##print(dicts_list)
        ##print("debug 2")
        return dicts_list



    def from_json(self, list_of_dict):
        
        players = []
        for player_dict in list_of_dict:
            player = Player(player_dict['nickname'], player_dict["email"], player_dict["date_of_birth"],player_dict["xp"], player_dict["class"])
            players.append(player)
        ##print(players)
        return players


    def from_xml(self, xml_string):
        players = []
        x = 0
        root = ET.Element("data")
        print(root.tag)
        for child in root:
            player = Player(nickname = root[x][0].text, emal=root[x][1].text, date_of_birth=root[x][2].text, xp = root[x][3].text, cls = root[x][4].text)
            x+=1
            players.append(player)
        return players

    def to_xml(self, list_of_players):

            ##tree = ET.parse(xml_string)
            root = ET.Element("data")
            for player in list_of_players:
                i = ET.SubElement(root, "player")
                ##print(i)
                name = ET.SubElement(i, "nickname")
                name.text = player.nickname
                ##print(name)
                email = ET.SubElement(i, "email")
                email.text = str(player.email)
                ##print(email)
                date = ET.SubElement(i, "date_of_birth")
                date.text = player.date_of_birth.strftime("%Y-%m-%d")
                ##print(date)
                xp = ET.SubElement(i, "xp")
                xp.text = str(player.xp)
                ##print(xp)
                cls = ET.SubElement(i, "class")
                cls.text = player.cls
            xml_string = ET.tostring(root, encoding='utf-8', method='xml')
            return xml_string.decode('utf-8')

    def from_protobuf(self, binary):
            player_list = []
            try:
                player_message = Player()  
                player_message.ParseFromString(binary) 
                for player in player_message.players:
                    player_obj = Player() 
                    player_obj.nickname = player.nickname
                    player_obj.email = player.email
                    player_obj.date_of_birth = player.date_of_birth
                    #print(player.date_of_birth)
                    player_obj.xp = player.xp
                    player_obj.cls = player.cls
                    player_list.append(player_obj)
                    #print(player_list)
            except Exception as e:
                pass
            return player_list

    def to_protobuf(self, list_of_players):
        players_list = player_pb2.PlayersList()
        for player in list_of_players:
            proto_player = players_list.player.add()
            setattr(proto_player, 'nickname', player.nickname)
            setattr(proto_player, 'email', player.email)
            setattr(proto_player, 'date_of_birth', player.date_of_birth.strftime("%Y-%m-%d"))
            setattr(proto_player, 'xp', player.xp)
            setattr(proto_player, 'cls', getattr(player_pb2.Class, player.cls))

        return players_list.SerializeToString()
    

