import discord
import os
import random
import asyncio
import time
from discord.ext import commands
from keep_alive import keep_alive

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(
        name='Prend son service...'))
    print('We have logged in as {0.user}'.format(client))


async def change_status():
    await client.wait_until_ready()
    # Définition de la liste de statuts
    statuses = [
        'Surveille la prison', 'Observe...', 'Fait le maton',
        'Récolte les pots de vins', 'Astique sa matraque',
        "S'entraine à punir", "!help", 'Sévit sur la prison',
        'Regarde les caméras', 'Se balade dans les douches',
        'Prend sa pose café', 'Fait une ronde', 'Se balade dans la cour',
        'Acceuil des détenus', 'Inspecte les cellules'
    ]

    while not client.is_closed():
        # Choix aléatoire du statut
        status = random.choice(statuses)

        await client.change_presence(activity=discord.Game(name=status))

        await asyncio.sleep(300)


@client.command()
@commands.has_permissions(manage_roles=True)
async def create_role(ctx):

    guild = ctx.guild
    # Définition du nom du role
    name = 'Prisonnier'
    # Création du role
    role = await guild.create_role(name=name)
    role.hoist = True
    # Envoi de la confirmation de création du role
    await ctx.send(f'Role `{name}` has been created')


@client.command()
async def roles(ctx):  # Renvoie la liste des roles du serveur
    return ([(r.name) for r in ctx.guild.roles])


@client.command()
async def roles_membre(member):  # Renvoie la liste des id des roles du membre
    return ([(r.id) for r in member.roles])


@client.command()
# Renvoie la liste des noms des roles du membre
async def noms_roles_membre(member):
    return ([(r.name) for r in member.roles])


@client.command()
async def lst_categories(ctx):  # Renvoie la liste des catégories du serveur
    return ([(r.name) for r in ctx.guild.categories])


@client.command()
# Renvoie la liste des channel vocaux du serveur
async def lst_voice_channels(ctx):
    return ([(r.name) for r in ctx.guild.voice_channels])


@client.command()
async def update_role(ctx, name):  # Mets à jour le role passé en paramètre
    role = discord.utils.get(ctx.guild.roles, name=name)
    await role.edit(speak=False)
    role.hoist = True
    return None


@client.command()
async def prison(ctx, member: discord.Member, temps=60):

    channel_origin = member.voice.channel.name  # Salon vocal du membre
    max_temps = 600  # Temps de prison max
    list_role = await roles(ctx)  # Liste des roles du serveur
    # Sauvegarde des roles du membre
    nom_role_membre = await noms_roles_membre(member)

    """
    Pré-réquis
    """
    await update_role(ctx, '@everyone')

    if 'Prisonnier' not in list_role:
        await create_role(ctx)  # Créer un role 'Prisonnier'
    await update_role(ctx, 'Prisonnier')

    """
    Conditions à vérifier
    """

    if temps > max_temps:
        return await ctx.send(f'Oh là, calme toi Cowboy, laisse lui sa liberté d\'expression ! {temps} > {max_temps}')

    if 'Prisonnier' in nom_role_membre:
        return await ctx.send(f'Mais c\'est du harcèlement ! Laisse le `{member.name}` est déjà prisonnier !')

    """
    Début des actions
    """
    for i in nom_role_membre:  # Bloc de suppression de tous les roles du membre
        role = discord.utils.get(member.guild.roles, name=f"{i}")
        if str(role) != "@everyone":
            await member.remove_roles(role)

    role = discord.utils.get(member.guild.roles, name="Prisonnier")

    await member.add_roles(role)  # Ajout du role Prisonnier au membre

    # Création de la catégorie Prison
    if 'Prison' not in await lst_categories(ctx):
        await ctx.guild.create_category('Prison')

    # Création du salon vocal Cellule
    if 'Cellule' not in await lst_voice_channels(ctx):
        category = discord.utils.get(ctx.guild.categories, name='Prison')
        await ctx.guild.create_voice_channel('Cellule', category=category)

    await member.edit(mute=True)  # Mute l'utilisateur

    # Déplace l'utilisateur vers la cellue
    await member.move_to(discord.utils.get(ctx.guild.voice_channels, name='Cellule'))

    await asyncio.sleep(temps)  # Temps d'emprisonnement


    """
    Libération 
    """
    await member.edit(mute=False)  # Unmute l'utilisateur
    await member.remove_roles(discord.utils.get(member.guild.roles, name="Prisonnier")) #Supprime le role Prisonnier
    # Ecrit un message de confirmation de libération
    await ctx.send(f"{member.name} a été libéré !")

    # Renvoie le membre à son salon vocal d'origine
    await member.move_to(discord.utils.get(ctx.guild.voice_channels, name=channel_origin))

    for i in nom_role_membre:  # Bloc de réattribution des roles
        role = discord.utils.get(member.guild.roles, name=f"{i}")
        if str(role) != "@everyone":
            await member.add_roles(role)
    


# Execute en boucle la fonction change_status()
client.loop.create_task(change_status())

# Script pour maintenir le bot en vie
keep_alive()

# Permet de lancer le bot
client.run(os.getenv('TOKEN'))
