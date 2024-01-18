import sqlite3
from riotwatcher import LolWatcher
from image_class import Profil, Match



lol_watcher = LolWatcher("RGAPI-a1155084-378c-46af-8881-8b7c6c886581")
info = lol_watcher.summoner.by_name("euw1", "raphalefou79")

puuid = info["puuid"]
matchid = lol_watcher.match.matchlist_by_puuid(region="euw1", puuid=puuid, count=1) #Utilise l'API pour retrouver l'ID du dernier match

match = lol_watcher.match.by_id(match_id=matchid[0], region="euw1")







db = sqlite3.connect("database.sqlite3")

cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS follow(pseudo, region, matchid)")



def test(pseudo: str, region: str, matchid): 
    try:
        cur.execute("SELECT pseudo, region FROM follow WHERE pseudo = (?) AND region = (?)", (pseudo, region))
        result = cur.fetchone()

        
        if result:
            print("Vous suivez déjà ce joueur !")
        
        else:
                 
            player_insert = "INSERT INTO follow(pseudo, region, matchid) VALUES (?, ?, ?)"
            data = (pseudo, region, matchid)
            
            cur.execute(player_insert, data)
            db.commit()
            
            
    except sqlite3.Error as e:
        print(f'Erreur SQLite : {e}')

player = Profil('euw1','raphalefou79')

matchid = lol_watcher.match.matchlist_by_puuid(region='EUW1', puuid= player.getPuuidPlayer(), count=1)

# test('raphalefou79','euw1','10')

cur.execute("UPDATE follow SET matchid = ? WHERE matchid = 10", ('100',))
db.commit()
    
    
    # if pseudo in liste_player.keys():
    #     await ctx.send(f'Vous suivez déjà ce joueur ! Vous pouvez regarder qui vous suivez avec la commande : **!fil-player**')

    # else:

    #     info = lol_watcher.summoner.by_name(region_set, pseudo)
    #     puuid = info["puuid"]
    #     player = Profil(region_set, pseudo)
        
    #     matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1)
    #     print("cc")       
    #     await ctx.send("Joueur choisi, en attente d'un nouveau match ! Vous pouvez arretez de suivre un joueur avec : **!stop-follow <player>**")            
                
        
    #     while True:

            
    #             liste_player[pseudo] = region_set
    #             #Vérifie si le joueur est déjà suivi 
                

    #             temp = matchid
                
    #             matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1) #Utilise l'API pour retrouver l'ID du dernier match
    #             previous_lp = player.lp()

    #             if matchid != temp:
    #                 actual_lp = player.lp()
                    
    #                 lpGain = previous_lp - actual_lp
    #                 if lpGain == 0:
    #                     lpGain = "?"
                        
    #                 elif lpGain > 0:
    #                     lpGain = "+"+str(lpGain)
                        
    #                 if lpGain == None:
    #                     lpGain = "?"
    #                 # Calcul le gain de LP
                    
                    
                    
    #                 statsImage(region_set, pseudo, matchid[0], str(lpGain)) # Met les stats du match en image
    #                 await ctx.send(file=discord.File('home/debian/discord_bot_lol/img/match/match'+ matchid[0]+'.png'))

    #             await asyncio.sleep(30)