import discord
from discord import app_commands
from discord.ext import commands

from discordToken import discordToken

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await client.wait_until_ready()
    await tree.sync()
    print("Connected, checking for commands")
    
@tree.command(name="help")
async def help(ctx):
    await ctx.channel.send("/createchannels arg1: num_of_teams arg2: team, names, separated")
    
    await ctx.channel.send("/cleanup - clears server")

@tree.command(name="createchannels")
async def createchannels(ctx, channelnumber: int, listofclansarg: str):
    clanlist = [clan.strip() for clan in listofclansarg.split(',')]
    
    if len(clanlist) == int(channelnumber):
        ClansList = []
        await ctx.channel.send(f"Creating categories: {clanlist}")

        for clan in clanlist:
            # Create category
            category = await ctx.guild.create_category(clan)

            ClansList.append(category)
            
            # Deny all roles access to the category
            await category.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)

            # Create roles and give access to the category
            role = await ctx.guild.create_role(name=f"{clan}_role")
            await category.set_permissions(role, read_messages=True, connect=True)

            await ctx.channel.send(f"Creating channels for: {clan}")

            # Create text and voice channels within the category
            await ctx.guild.create_text_channel(clan+"_general", category=category)
            await ctx.guild.create_voice_channel(clan+"_voice", category=category)

        await ctx.channel.send("Categories and channels created")

        # Create "leaders" category
        leaders_category = await ctx.guild.create_category("leaders")

        # Deny all roles access to the leaders category
        await leaders_category.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)

        # Create roles and give access to the leaders category
        leaders_role = await ctx.guild.create_role(name="leaders_role")
        
        await leaders_category.set_permissions(leaders_role, read_messages=True, connect=True)
        
        for category in ClansList:
            await category.set_permissions(leaders_role, read_messages=True, connect=True)
        
        await ctx.channel.send("Leaders category and channels created")

        # Create text and voice channels within the leaders category
        await ctx.guild.create_text_channel("leaders_general", category=leaders_category)
        await ctx.guild.create_voice_channel("leaders_voice", category=leaders_category)

    else:
        await ctx.channel.send(f"Incorrect amount of clans: I've gotten {len(clanlist)} clans, but {channelnumber} were expected")

@tree.command(name='cleanup',description="CleanUp your discord server!")
async def raid(ctx: commands.Context):
    allObjects = []
    for guild in client.guilds:
        for someObject in [guild.roles, guild.text_channels, guild.voice_channels, guild.categories]:
            for exactObject in someObject:
                allObjects.append(exactObject)
        for exactObject in allObjects:
            try:
                await exactObject.delete()
                print(f'| Object has been successfully deleted - {exactObject.id}')
            except:
                print(f'| I could not delete some object - {exactObject.id}')

        await ctx.guild.create_category("base")
        category = discord.utils.get(ctx.guild.categories, name="base")
        await ctx.guild.create_text_channel("base_gen", category=category)

client.run(discordToken)