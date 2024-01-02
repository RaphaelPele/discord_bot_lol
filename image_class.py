from PIL import Image, ImageDraw, ImageFont, ImageFilter
from riotwatcher import LolWatcher, ApiError



lol_watcher = LolWatcher("RGAPI-4b82fca5-d98f-4214-a03a-594c7e62de2e")
region = "euw1"



class Profil:
    
    region:str
    pseudo:str
    
    def __init__(self, region, pseudo) -> None:
        
        self.region = region
        self.pseudo = pseudo
        self.queue = "RANKED_SOLO_5x5"
        self.region_list = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "TR1", "OC1", "TR1", "RU", "PH2", "SG2", "TH2", "TW2", "VN2"]


    def getIdPlayer(self):
        """Return ID player

        Returns:
            str: player_id
        """
        
        info = lol_watcher.summoner.by_name(self.region.upper(), self.pseudo)
        
        player_id = info['id']
        
        return player_id
    

    def isRegionValid(self):
        """Vérifie si la région saisie existe

        Returns:
            bool: True si elle est existe
        """
        region = self.region.upper()
        
        if region in self.region_list:
            return True
        else:
            return False

    

    def classement(self):
        """Classement du joueur recherché

        Returns:
            tuple: (pseudo, tier(gold), rank(4), leaguePoints, wins, losses)
        """
        if self.isRegionValid() == True:
            
            # Renvoi les stats de ranked du joueur
            my_ranked_stats = lol_watcher.league.by_summoner(self.region.upper(), self.getIdPlayer())
            
            # Parcourt les dictionnaire de my_ranked_stats pour trouver les stats de la RANKED_SOLO_5x5
            for index, dictionnaire in enumerate(my_ranked_stats):
                if dictionnaire["queueType"] == self.queue:
                    
                    return (my_ranked_stats[index]["summonerName"], my_ranked_stats[index]["tier"], my_ranked_stats[index]["rank"], my_ranked_stats[index]["leaguePoints"], my_ranked_stats[index]["wins"], my_ranked_stats[index]["losses"])
        else:
            return "Votre region est invalide"
        




class Match:
    
    puuid: str
    
    region: str
    pseudo: str

    kills: int
    deaths: int
    assists: int
    kda: float
    goldsEarned: int
    win: bool
    gameDuration: int #seconds
    champion: str
    
    def __init__(self, region, pseudo, match_id) -> None:
        self.region = region
        self.pseudo = pseudo
        
        info = lol_watcher.summoner.by_name(self.region.upper(), self.pseudo)
        self.puuid = info["puuid"]
        self.queue = "RANKED_SOLO_5x5"
        
        self.fill(match_id)
        
        
    def fill(self, match_id: str):
        match = lol_watcher.match.by_id(match_id=match_id, region=self.region)
        
        
        if match is None:
            raise Exception("Match not found")
        
        player_index: int = -1
        for x, dictionnaire in enumerate(match["info"]["participants"]):
            if dictionnaire["puuid"] == self.puuid:
                player_index = x
                
        if player_index == -1:
            raise Exception("Player not found in the match")
        
        self.configure(
            match["info"]["participants"][player_index]["kills"],
            match["info"]["participants"][player_index]["deaths"],
            match["info"]["participants"][player_index]["assists"],
            match["info"]["participants"][player_index]["challenges"]["kda"],
            match["info"]["participants"][player_index]["goldEarned"],
            match["info"]["participants"][player_index]["win"],
            match["info"]["gameDuration"],
            match["info"]["participants"][player_index]["championName"])
            
    
    def configure(self, 
                  kills: int, 
                  deaths: int, 
                  assists: int, 
                  kda: float, 
                  goldsEarned: int, 
                  win: bool, 
                  gameDuration: int, 
                  champion: str):
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.kda = kda
        self.goldsEarned = goldsEarned
        self.win = win
        self.gameDuration = gameDuration
        self.champion = champion
    
    
    def get_champion_icon_path(self)-> str:
        return "img/champIcon/" + self.champion + "Square.png"       
        
          
          

def statsImage(region:str,pseudo:str,match_id:str):
    """Create image that show stats of the player for the match

    Args:
        region (str): server of tha match
        pseudo (str): pseudo of player
        match_id (str): id of match
    """
    match = Match(region, pseudo, match_id)
    
    
    color = (158,145,142)
    font = ImageFont.truetype('arial', 18)
    coordonnes = {'kills': (291, 21), 'deaths': (326,21), 'assists': (359, 21), 'win': (23,60), 'kda': (305,45), 'goldsEarned': (460,15), 'gameDuration' : (23,80)}
    
    # Affiche le temps en minute et en secondes
    minutes = match.gameDuration // 60
    secondes = match.gameDuration % 60
    gametime = f'{minutes}:{secondes}'
    
    # Si win = True -> écrire Victory
    if match.win == True:
        imgResult = Image.open(r"img\opgg_win_template.png")
        imgResult = imgResult.convert("RGBA")
        draw = ImageDraw.Draw(imgResult)
        draw.text(coordonnes['win'], 'Victory', font= font, fill='gray')
    
    # Si win = False -> Defeat   
    else:
        imgResult = Image.open(r"img\opgg_lose_template.png")
        imgResult = imgResult.convert("RGBA")
        draw = ImageDraw.Draw(imgResult)
        draw.text(coordonnes['win'], 'Defeat', font= font, fill='gray')
    
    # Toutes les données à écrire
    draw.text(coordonnes['kills'],str(match.kills), font= font, fill=color)
    draw.text(coordonnes['deaths'], str(match.deaths), font= font, fill=color)
    draw.text(coordonnes['assists'], str(match.assists), font= font, fill=color)
    draw.text(coordonnes['goldsEarned'],f"Golds earned : {match.goldsEarned}", font= font, fill=color)
    draw.text(coordonnes['kda'],f"KDA {match.kda}", font= font, fill=color)
    draw.text(coordonnes['gameDuration'],str(gametime), font=font, fill=color)
    
    # champion icon
    championIcon = Image.open(match.get_champion_icon_path())
    championIcon = championIcon.convert("RGBA")
    championIcon= championIcon.resize((80,80))  
    
    
    # mask for circulate image
    mask = Image.new('L', (80,80), 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + (80,80), fill=255)
    championIcon.putalpha(mask)
    
    imgResult.alpha_composite(championIcon, (180,10))

    imgResult.save('img/match/match'+match_id+'.png', 'png')
    


info = lol_watcher.summoner.by_name("euw1", "raphalefou79")
puuid = info["puuid"]

region = "euw1"
player = "raphalefou79"

matchlist = lol_watcher.match.matchlist_by_puuid(region="euw1", puuid=puuid, count=5, queue=420)
for match_id in matchlist:
    match = Match(region, player, match_id)
    statsImage(region, player, match_id)


player1 = Profil("euw1", "raphalefou")
print(player1.classement())