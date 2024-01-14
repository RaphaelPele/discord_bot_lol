import discord
import os
from riotwatcher import LolWatcher, ApiError
from discord.ext import commands, tasks
from image_class import statsImage, Profil
import asyncio

liste_player = {}

token = ""
intents = discord.Intents.all()
intents.messages = True    
bot = commands.Bot(command_prefix="!", intents=intents)
# channel = bot.get_channel(1188907878065651845)

lol_watcher = LolWatcher("RGAPI-a1155084-378c-46af-8881-8b7c6c886581")
region_set = "na1"

@bot.event
async def on_ready():
        print(f'Logged on as {bot.user}!')


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

    if pseudo in liste_player.keys():
        await ctx.send(f'Vous suivez déjà ce joueur ! Vous pouvez regarder qui vous suivez avec la commande : **!fil-player**')

    else:

        info = lol_watcher.summoner.by_name(region_set, pseudo)
        puuid = info["puuid"]
        player = Profil(region_set, pseudo)
        
        matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1)
        print("cc")       
        await ctx.send("Joueur choisi, en attente d'un nouveau match ! Vous pouvez arretez de suivre un joueur avec : **!stop-follow <player>**")            
                
        
        while True:

            
                liste_player[pseudo] = region_set
                #Vérifie si le joueur est déjà suivi 
                

                temp = matchid
                
                matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1) #Utilise l'API pour retrouver l'ID du dernier match
                previous_lp = player.lp()

                if matchid != temp:
                    actual_lp = player.lp()
                    
                    lpGain = previous_lp - actual_lp
                    if lpGain == 0:
                        lpGain = "?"
                        
                    elif lpGain > 0:
                        lpGain = "+"+str(lpGain)
                        
                    if lpGain == None:
                        lpGain = "?"
                    # Calcul le gain de LP
                    
                    
                    
                    statsImage(region_set, pseudo, matchid[0], str(lpGain)) # Met les stats du match en image
                    await ctx.send(file=discord.File('home/debian/discord_bot_lol/img/match/match'+ matchid[0]+'.png'))

                await asyncio.sleep(30)


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



bot.run(token)
