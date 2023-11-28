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

@tree.command(name="kickteam", description="Kicks all members with specified team role")
@commands.has_role("admin")
async def kickTeam(ctx: commands.Context, role: discord.Role):
    for member in role.members:
        await member.kick()
        await ctx.channel.send(f"Kicked {member.display_name}")

# Define a list of role and channel names that should not be deleted
protected_roles = ["Admin", "DiXX_role"]
protected_channels = ["dixx_general", "DiXX_voice", "DiXX"]

@tree.command(name='cleanup', description="CleanUp your discord server!")
async def raid(ctx: commands.Context):
    # Kick members not in protected roles
    for member in ctx.guild.members:
        if any(role.name in protected_roles for role in member.roles):
            continue  # Skip kicking members with protected roles
        try:
            await member.kick()
            await ctx.channel.send(f"Kicked {member.display_name}")
        except:
            print(f"| I could not kick {member.display_name}")
    
    # Get all roles, channels, and categories in the guild
    all_objects = []
    for guild in client.guilds:
        for some_object in [guild.roles, guild.text_channels, guild.voice_channels, guild.categories]:
            for exact_object in some_object:
                all_objects.append(exact_object)

    # Iterate through all objects and delete if not in the protected list
    for exact_object in all_objects:
        try:
            # Check if the object is in the protected list
            if exact_object.name in protected_roles or exact_object.name in protected_channels:
                print(f"| Skipping deletion of protected object - {exact_object.name} ({exact_object.id})")
            else:
                await exact_object.delete()
                print(f"| Object has been successfully deleted - {exact_object.name} ({exact_object.id})")
        except:
            print(f"| I could not delete some object - {exact_object.name} ({exact_object.id})")

    # Create a category and a text channel after cleanup
    await ctx.guild.create_category("base")
    category = discord.utils.get(ctx.guild.categories, name="base")
    await ctx.guild.create_text_channel("base_gen", category=category)

client.run(discordToken)