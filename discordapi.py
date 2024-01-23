import discord
import os
from riotwatcher import LolWatcher, ApiError
from discord.ext import commands, tasks
import sqlite3
from image_class import statsImage, Profil
import asyncio
from config import api_key_discord, api_key_lol


token = api_key_discord
intents = discord.Intents.all()
intents.messages = True    
bot = commands.Bot(command_prefix="!", intents=intents)
# channel = bot.get_channel(1188907878065651845)

#Création de la base de donnée qui stock les joueurs
db = sqlite3.connect("database.sqlite3")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS follow(pseudo STR, region STR, matchid STR, puuid STR, channel_id)")
#Création de la base de donnée qui stock les joueurs

#Connexion à l'api Riot Games
lol_watcher = LolWatcher(api_key_lol)
region_set = "na1"


@bot.event
async def on_ready():
        print(f'Logged on as {bot.user}!')
        follow_send.start()
        

     
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
        
        await ctx.send(file=discord.File('/home/debian/discord_bot_lol/img/match'+ match_id+'.png'))



@bot.command(name="follow")
async def follow(ctx, region_set, pseudo):


    try:
        channel = ctx.channel.id
        cur.execute("SELECT pseudo, region FROM follow WHERE pseudo = (?) AND region = (?) AND channel_id = (?)", (pseudo, region_set, channel))
        result = cur.fetchone()
        
        if result:
            await ctx.send("Vous suivez **déjà** ce joueur !")
        
        else:
            
            player = Profil(region_set, pseudo)
            puuid = player.getPuuidPlayer()
            matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1, queue=420)
            
            await ctx.send("Joueur choisi, en attente d'un nouveau match ! Vous pouvez arretez de suivre un joueur avec : **!stop-follow <player>**")  
                      
            player_insert = "INSERT INTO follow(pseudo, region, matchid, puuid, channel_id) VALUES (?, ?, ?, ?, ?)"
            data = (pseudo, region_set, matchid[0], puuid, channel)
            
            cur.execute(player_insert, data)
            db.commit()
            
    except ApiError as e:
        if e.response.status_code == 429:
            await ctx.send("Trop de requêtes, veuillez patientez avant de réessayer.")
        
        if e.response.status_code == 404:
            await ctx.send('Aucun compte trouvé, vérifiez les paramètres que vous avez saisi et respectez la syntaxe suivante : **!follow <region> "<pseudo>"')
            
    except sqlite3.Error as e:
        print(f'Erreur SQLite : {e}')


@bot.command(name="followed-player")
async def fil_player(ctx):
    
    liste_player = []
    channel_id = ctx.channel.id
    cur.execute("SELECT pseudo FROM follow WHERE channel_id = ?", (channel_id,))
    players = cur.fetchall()
    
    if players:
        for row in players:
            liste_player.append(row[0])
            x = ", ".join(liste_player)
        await ctx.send(f'Vous suivez actuellement : **{x}**')
        
    else:
        await ctx.send("Vous ne suivez **personne** !")

        
        
@bot.command(name="stop-follow")
async def stop_follow(ctx, pseudo):
    
    channel_id = ctx.channel.id
    cur.execute("DELETE FROM follow WHERE pseudo = ? AND channel_id = ?", (pseudo, channel_id))
    db.commit()
    
    await ctx.send(f'Le joueur **{pseudo}** a été supprimé !')



@tasks.loop(seconds= 30)
async def follow_send():
    
    # print("Tache follow")
    cur.execute("SELECT * FROM follow")
    rows = cur.fetchall() #Liste des joueurs à parcourir
    
    for row in rows:
        
        previous_matchid = row[2]
        present_matchid = lol_watcher.match.matchlist_by_puuid(region= row[1], puuid= row[3], count= 1, queue=420) #Regarde si le joueur a fait un nouveau match
        # print(row[0])
        if previous_matchid != present_matchid[0]:
            
            try:
                cur.execute("UPDATE follow SET matchid = ? WHERE matchid = ? AND pseudo = ?", (present_matchid[0], previous_matchid, row[0]))
                db.commit()
            except Exception as e:
                print(f"Erreur lors de la mise à jour de la base de données : {e}")

            # print(row[2])
            statsImage(row[1], row[0], present_matchid[0]) # Met les stats du match en image
            print(f"Updating for {row[0]} {previous_matchid} -> {present_matchid[0]}")
            
            channel = bot.get_channel(row[4]) #Récupère l'ID du channel pour envoyer le message au bon endroit
            # print("test")
            
            try:
                await channel.send(file=discord.File(r'/home/debian/discord_bot_lol/img/match/match'+ present_matchid[0]+'.png'))
            except Exception as e:
                print(f"Erreur lors de l'envoi du fichier : {e}")



        


bot.run(token)

