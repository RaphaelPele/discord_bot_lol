import discord
from riotwatcher import LolWatcher, ApiError
from discord.ext import commands
from image_class import statsImage, Profil
import asyncio

token = "MTE4ODk2NzEzMTgwMzU2NjIwMw.GE4Egf.6R5aC_4DdydmOnB0HLpkujU4brEyjxu502e89Q"
intents = discord.Intents.all()
intents.messages = True    
bot = commands.Bot(command_prefix="!", intents=intents)
channel = bot.get_channel(1188907878065651845)

lol_watcher = LolWatcher("RGAPI-4b82fca5-d98f-4214-a03a-594c7e62de2e")
region = "na1"

@bot.event
async def on_ready():
        print(f'Logged on as {bot.user}!')


@bot.command(name="helpme")
async def help(ctx):
    await ctx.send('```Définir votre région: !my_region = <your_region> \nVoir votre profil: !profil <region> "<pseudo>"```')

     
    
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



@bot.command(name="fil")
async def fil(ctx, region_set, pseudo):
        info = lol_watcher.summoner.by_name(region_set, pseudo)
        puuid = info["puuid"]

        region = region_set
        player = pseudo

        matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1)
        
        await ctx.send("Joueur choisi, en attente d'un nouveau match")
        
        while True:
            temp = matchid
            
            matchid = lol_watcher.match.matchlist_by_puuid(region=region_set, puuid=puuid, count=1)

            if matchid != temp:
                statsImage(region, player, matchid[0]) # Met les stats du match en image
            
                await ctx.send(file=discord.File('img/match'+ matchid[0]+'.png'))
            
            else:
                await ctx.send('Aucun nouveau match')
            
            await asyncio.sleep(30)
        



bot.run(token)