import discord
import os
import random
import asyncio
from discord.ext import commands
from keep_alive import keep_alive

temps_max = {}

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(
        name='Prend son service...'))
    print('Nous sommes arrivé à la prison en tant que {0.user}'.format(client))


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


@commands.has_permissions(manage_roles=True)
async def create_role(ctx,name):
    guild = ctx.guild
    # Création du role
    role = await guild.create_role(name=name)
    role.hoist = True
    # Envoi de la confirmation de création du role
    await ctx.send(f'Role `{name}` has been created')


async def roles(ctx):  # Renvoie la liste des roles du serveur
    return ([(r.name) for r in ctx.guild.roles])


async def roles_membre(member):  # Renvoie la liste des id des roles du membre
    return ([(r.id) for r in member.roles])

# Renvoie la liste des noms des roles du membre
async def noms_roles_membre(member):
    return ([(r.name) for r in member.roles])


async def lst_categories(ctx):  # Renvoie la liste des catégories du serveur
    return ([(r.name) for r in ctx.guild.categories])


# Renvoie la liste des channel vocaux du serveur
async def lst_voice_channels(ctx):
    return ([(r.name) for r in ctx.guild.voice_channels])


# Renvoie la liste des channel textuels du serveur
async def lst_text_channels(ctx):
    return ([(r.name) for r in ctx.guild.text_channels])


async def update_role(ctx, name):  # Mets à jour le role passé en paramètre
    role = discord.utils.get(ctx.guild.roles, name=name)
    await role.edit(speak=False)
    role.hoist = True
    return None


async def suppr_roles(member, lst_roles):
    for i in lst_roles:  # Bloc de suppression de tous les roles du membre
        role = discord.utils.get(member.guild.roles, name=f"{i}")
        if str(role) != "@everyone":
            await member.remove_roles(role)
    return None


# Met en place la raison de l'emprisonnement
async def raison(reason):
    if len(reason)==0:
        reason = 'Pas de raison spécifiée'
    else:
        raison = ''
        for i in reason:
            raison+=i
            raison += ' '
        reason = raison
    return reason


# Met à jour tous les salons textuels
async def update_text(ctx,lst_salons):
    for i in lst_salons:
        channel = discord.utils.get(ctx.guild.text_channels, name=i)
        role = discord.utils.get(ctx.guild.roles, name="Prisonnier")
        await channel.set_permissions(role,send_messages=False)
    return None

# Met à jour tous les salons vocaux
async def update_voice(ctx,lst_salons):
    for i in lst_salons:
        channel = discord.utils.get(ctx.guild.voice_channels, name=i)
        role = discord.utils.get(ctx.guild.roles, name="Prisonnier")
        await channel.set_permissions(role,connect=False)
    return None

@client.command()
async def set_temps_max(ctx, temps):
    temps_max[ctx.guild.id] = int(temps)
    return None

async def get_max_temps(ctx):
    if ctx.guild.id in temps_max:
        max_temps = temps_max[ctx.guild.id]
    else:
        max_temps = 600  # Temps de prison max
    return max_temps

@client.command()
async def prison(ctx, member: discord.Member, temps=60, *reason):
    """
    Attribution des valeurs des variables
    """
    reason = await raison(reason)
    max_temps = await get_max_temps(ctx)
    list_role = await roles(ctx)  # Liste des roles du serveur
    # Sauvegarde des roles du membre
    nom_role_membre = await noms_roles_membre(member)
    try:
        channel_origin = member.voice.channel.name  # Salon vocal du membre
    except:
        channel_origin = None  # Le membre n'est pas connecté

    """
    Pré-réquis
    """
    await update_role(ctx, '@everyone')
    await update_text(ctx,await lst_text_channels(ctx))
    await update_voice(ctx,await lst_voice_channels(ctx))
    if 'Prisonnier' not in list_role:
        await create_role(ctx,'Prisonnier')  # Créer un role 'Prisonnier'
    await update_role(ctx, 'Prisonnier')

    # Création de la catégorie Prison
    if 'Prison' not in await lst_categories(ctx):
        await ctx.guild.create_category('Prison')

    category = discord.utils.get(ctx.guild.categories, name='Prison')

    # Création du salon textuel archiveprison
    if 'archiveprison' not in await lst_text_channels(ctx):
        await ctx.guild.create_text_channel('ArchivePrison', category=category)

    # Création du salon vocal Cellule
    if 'Cellule' not in await lst_voice_channels(ctx):
        await ctx.guild.create_voice_channel('Cellule', category=category)


    role = discord.utils.get(member.guild.roles, name="Prisonnier")
    archiveprison = discord.utils.get(
        ctx.guild.text_channels, name='archiveprison')
    """
    Conditions à vérifier
    """

    if temps > max_temps:
        return await archiveprison.send(f'Oh là, calme toi Cowboy, laisse lui sa liberté d\'expression ! {temps} > {max_temps}')

    if 'Prisonnier' in nom_role_membre:
        return await archiveprison.send(f'Mais c\'est du harcèlement ! Laisse le `{member.name}` est déjà prisonnier !')
    if ctx.message.author.top_role < member.top_role:
        return await archiveprison.send('Oh là, tu essayes d\'emprisonner qui? Respecte ton supérieur !')

    """
    Début des actions
    """
    await suppr_roles(member, nom_role_membre)

    await member.add_roles(role)  # Ajout du role Prisonnier au membre

    # Déplace l'utilisateur vers la cellue
    if not channel_origin == None:
        await member.edit(mute=True)  # Mute l'utilisateur
        await member.move_to(discord.utils.get(ctx.guild.voice_channels, name='Cellule'))
    await archiveprison.send(f' `{member.name}` viens d\'être emprisonné `{temps} secondes` pour `{reason}` ')

    await asyncio.sleep(temps)  # Temps d'emprisonnement

    """
    Libération 
    """

    # Supprime le role Prisonnier
    await member.remove_roles(discord.utils.get(member.guild.roles, name="Prisonnier"))
    
    # Ecrit un message de confirmation de libération
    await archiveprison.send(f"`{member.name}` a été libéré !")

    # Renvoie le membre à son salon vocal d'origine
    if not channel_origin == None:
        await member.edit(mute=False)  # Unmute l'utilisateur
        await member.move_to(discord.utils.get(ctx.guild.voice_channels, name=channel_origin))

    for i in nom_role_membre:  # Bloc de réattribution des roles
        role = discord.utils.get(member.guild.roles, name=f"{i}")
        if str(role) != "@everyone":
            await member.add_roles(role)
    return None


# Execute en boucle la fonction change_status()
client.loop.create_task(change_status())

# Script pour maintenir le bot en vie
keep_alive()

# Permet de lancer le bot
client.run(os.getenv('TOKEN'))
