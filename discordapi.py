import discord
import os
from riotwatcher import LolWatcher, ApiError
from discord.ext import commands, tasks
import sqlite3
from image_class import statsImage, Profil
import asyncio

liste_player = {}

token = "MTE4ODk2NzEzMTgwMzU2NjIwMw.G0zcRB.ylvS3C-lZYBcvaQfifRiCK9QW0VNrokvGsmG9g"
intents = discord.Intents.all()
intents.messages = True    
bot = commands.Bot(command_prefix="!", intents=intents)
# channel = bot.get_channel(1188907878065651845)

#Création de la base de donnée qui stock les joueurs
db = sqlite3.connect("database.sqlite3")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS follow(pseudo STR, region STR, matchid STR, puuid STR)")
#Création de la base de donnée qui stock les joueurs

#Connexion à l'api Riot Games
lol_watcher = LolWatcher("RGAPI-a1155084-378c-46af-8881-8b7c6c886581")
region_set = "na1"


@bot.event
async def on_ready():
        print(f'Logged on as {bot.user}!')
        follow_send.start()
        


@bot.command(name="helpme")
async def help(ctx):
    await ctx.send('```Définir votre région: !my_region = <your_region> \n Voir votre profil: !profil <region> "<pseudo>"```')

     
@bot.command(name="profil")
async def profil_lol(ctx, region_set, pseudo):
    player = Profil(region_set, pseudo)
    await ctx.send(f'**{player.classement()[0]}** est actuellement **{player.classement()[1]} {player.classement()[2]} {player.classement()[3]} LP** avec **{player.classement()[4]} victoires** et **{player.classement()[5]} défaites**')
    

@bot.command(name="history")
async def history_profil(ctx, region_set, nb_games, pseudo):
    
    info = lol_watcher.summoner.by_name(region_set, pseudo)
    puuid = info["puuid"]

    region = region_set
    player = pseudo

    matchlist = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=nb_games, queue=420)
    
    for match_id in matchlist[::-1]: #Parcourt la liste des match du plus vieux au plus recent
        
        statsImage(region, player, match_id) # Met les stats du match en image
        
        await ctx.send(file=discord.File('img/match'+ match_id+'.png'))



@bot.command(name="follow")
async def follow(ctx, region_set, pseudo):
    
    try:
        cur.execute("SELECT pseudo, region FROM follow WHERE pseudo = (?) AND region = (?)", (pseudo, region_set))
        result = cur.fetchone()
        
        if result:
            print("Vous suivez déjà ce joueur !")
        
        else:
            
            player = Profil(region_set, pseudo)
            puuid = player.getPuuidPlayer()
            matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1)
            
            await ctx.send("Joueur choisi, en attente d'un nouveau match ! Vous pouvez arretez de suivre un joueur avec : **!stop-follow <player>**")  
            
                      
            player_insert = "INSERT INTO follow(pseudo, region, matchid, puuid) VALUES (?, ?, ?, ?)"
            data = (pseudo, region_set, matchid[0], puuid)
            
            cur.execute(player_insert, data)
            db.commit()
            
            
    except sqlite3.Error as e:
        print(f'Erreur SQLite : {e}')


@bot.command(name="followed-player")
async def fil_player(ctx):
     await ctx.send(f'Vous suivez actuellement : {liste_player}')
        
        
@bot.command(name="stop-follow")
async def stop_follow(ctx, pseudo):
    if pseudo in liste_player:
        liste_player.remove(pseudo)
        await ctx.send(f'{pseudo} a été retiré des joueurs suivis !')
    else:
        await ctx.send(f"{pseudo} n'est pas dans la liste des joueurs suivis !")


@tasks.loop(seconds= 30)
async def follow_send():
    print("Tache follow")
    cur.execute("SELECT * FROM follow")
    rows = cur.fetchall() #Liste des joueurs à parcourir
    
    for row in rows:
        
        previous_matchid = row[2]
        present_matchid = lol_watcher.match.matchlist_by_puuid(region= row[1], puuid= row[3], count= 1) #Regarde si le joueur a fait un nouveau match

        if previous_matchid != present_matchid[0]:
            cur.execute("UPDATE follow SET matchid = ? WHERE matchid = ?", (present_matchid[0], previous_matchid[0]))
            print('test')
            statsImage(row[1], row[0], present_matchid) # Met les stats du match en image


        


bot.run(token)
