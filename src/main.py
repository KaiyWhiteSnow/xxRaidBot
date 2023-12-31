import discord
from discord import app_commands
from discord.ext import commands
import asyncio

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
@commands.has_role("Admin")
async def help(ctx):
    await ctx.channel.send("/createchannels arg1: team, names, separated")
    await ctx.channel.send("/cleanup - clears server")

@tree.command(name="createchannels")
@commands.has_role("Admin")
async def createchannels(ctx, listofclansarg: str):
    clanlist = [clan.strip() for clan in listofclansarg.split(',')]
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
        await asyncio.sleep(1)  # Introduce a 1-second delay
        await ctx.guild.create_voice_channel(clan+"_voice", category=category)
        await asyncio.sleep(1)  # Introduce a 1-second delay

        await ctx.channel.send(f"Channels created for: {clan}")

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
    await asyncio.sleep(1)  # Introduce a 1-second delay
    await ctx.guild.create_voice_channel("leaders_voice", category=leaders_category)

    await ctx.channel.send("Leaders channels created")

@tree.command(name="kickteam", description="Kicks all members with specified team role")
@commands.has_role("Admin")
async def kickTeam(ctx: commands.Context, role: discord.Role):
    for member in role.members:
        await member.kick()
        await ctx.channel.send(f"Kicked {member.display_name}")

# Define a list of role and channel names that should not be deleted
protected_roles = ["Admin", "DiXX_role"]
protected_channels = ["dixx_general", "DiXX_voice", "DiXX", "base", "base_gen"]

@tree.command(name='cleanup', description="CleanUp your discord server!")
@commands.has_role("Admin")
async def raid(ctx: commands.Context):
    # Fetch all members in the guild
    members = [member async for member in ctx.guild.fetch_members(limit=None)]

    # Kick members not in protected roles concurrently
    kick_tasks = [
        member.kick(reason="Cleanup") for member in members
        if not any(role.name in protected_roles for role in member.roles)
    ]
    await asyncio.gather(*kick_tasks)

    # Get all roles, channels, and categories in the guild
    all_objects = list(ctx.guild.roles) + list(ctx.guild.text_channels) + list(ctx.guild.voice_channels) + list(ctx.guild.categories)

    # Create a list to hold the tasks for object deletion
    delete_tasks = []

    # Iterate through all objects and schedule deletion tasks if not in the protected list
    for exact_object in all_objects:
        try:
            # Check if the object is in the protected list
            if exact_object.name in protected_roles or exact_object.name in protected_channels:
                print(f"| Skipping deletion of protected object - {exact_object.name} ({exact_object.id})")
            else:
                # Create a task for the deletion with a delay
                task = asyncio.create_task(delete_with_delay(exact_object))
                delete_tasks.append(task)
        except (discord.Forbidden, discord.HTTPException) as e:
            print(f"| Error deleting object - {exact_object.name} ({exact_object.id}): {e}")
    
    try:
        # Wait for all delete tasks to complete
        await asyncio.gather(*delete_tasks)
    except discord.errors.HTTPException as e:
        print(f"| Error during cleanup: {e}")


# Function to delete an object with a delay
async def delete_with_delay(obj):
    await asyncio.sleep(1)  # 1 second delay
    await obj.delete()
    print(f"| Object has been successfully deleted - {obj.name} ({obj.id})")


client.run(discordToken)