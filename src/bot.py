import os
import time
import random
import datetime
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord_slash import cog_ext, utils
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

from mentor import *
from compiler import *
from instagram import *


load_dotenv()
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)
slash = SlashCommand(bot, sync_commands=False)

GUILD_ID = int(os.environ['GUILD_ID'])
BOT_ID = int(os.environ['BOT_ID'])
BOT_TOKEN = os.environ['BOT_TOKEN']

CHANNEL_ANNOUNCEMENTS = int(os.environ['CHANNEL_ANNOUNCEMENTS'])
CHANNEL_ANNOUNCEMENTS_RR = int(os.environ['CHANNEL_ANNOUNCEMENTS_RR'])
CHANNEL_ANNOUNCEMENTS_EC = int(os.environ['CHANNEL_ANNOUNCEMENTS_EC'])
CHANNEL_UNASSIGNED = int(os.environ['CHANNEL_UNASSIGNED'])
CHANNEL_WELCOME = int(os.environ['CHANNEL_WELCOME'])
CHANNEL_BOT_TEST = int(os.environ['CHANNEL_BOT_TEST'])
CHANNEL_SELECTION_YEAR = int(os.environ['CHANNEL_SELECTION_YEAR'])
CHANNEL_SELECTION_TOPIC = int(os.environ['CHANNEL_SELECTION_TOPIC'])
CHANNEL_SELECTION_CAMPUS = int(os.environ['CHANNEL_SELECTION_CAMPUS'])

ROLE_UNASSIGN = int(os.environ['ROLE_UNASSIGN'])
ROLE_BOT_DEV = int(os.environ['ROLE_BOT_DEV'])
ROLE_MOD = int(os.environ['ROLE_MOD'])
ROLE_CORE_RR = int(os.environ['ROLE_CORE_RR'])
ROLE_CORE_EC = int(os.environ['ROLE_CORE_EC'])
ROLE_FIRSTYEAR = int(os.environ['ROLE_FIRSTYEAR'])
ROLE_SECONDYEAR = int(os.environ['ROLE_SECONDYEAR'])
ROLE_THIRDYEAR = int(os.environ['ROLE_THIRDYEAR'])
ROLE_FOURTHYEAR = int(os.environ['ROLE_FOURTHYEAR'])
ROLE_GRAD = int(os.environ['ROLE_GRAD'])
ROLE_CAMPUS_RR = int(os.environ['ROLE_CAMPUS_RR'])
ROLE_CAMPUS_EC = int(os.environ['ROLE_CAMPUS_EC'])
ROLE_CAMPUS_OUTSIDER = int(os.environ['ROLE_CAMPUS_OUTSIDER'])

CONFESSIONS = dict()

MENTOR_SYNC_TIME = 0

async def remindUnassignedRoleMembers():
    unassigned_channel = bot.get_channel(CHANNEL_UNASSIGNED)
    await unassigned_channel.purge(limit=1)
    content = f'''Hello <@&{ROLE_UNASSIGN}>! Please do read these instructions.\n
1. <#{CHANNEL_SELECTION_YEAR}> channel has been added to select the year you are in. Once you select your batch you will also be given access to a batch specific text channel, so you can communicate with your batchmates. Since some of our activities are in teams, we felt the need to create a shared space where batchmates can get together and form teams and communicate for events such as hackathons and projects.\n
2. <#{CHANNEL_SELECTION_CAMPUS}> will allow you to choose your campus. Please select the correct campus, since you will be given access to campus specific text channels and will be notified about events at your campus.\n
3. <#{CHANNEL_SELECTION_TOPIC}> has been added to allow you to choose the domains you are interested in. This will help you find like minded peers with similar interests to team up and have discussions with. It is advisable to choose a maximum of 3 topics, however you are free to choose as many as you like.'''
    await unassigned_channel.send(content)


async def syncMentorInformation():
    global MENTOR_SYNC_TIME
    MENTOR_SYNC_TIME = int(time.time())
    readDataFrame()
    initialiseMentorFilters()


@bot.event
async def on_ready():
    global CONFESSIONS
    global compiler_keys
    CONFESSIONS = dict()

    online_embed = discord.Embed(title="I am back", color=discord.Color.blue())
    await bot.get_channel(CHANNEL_BOT_TEST).send(embed=online_embed)

    for client_id, client_secret in compiler_keys.keys():
        compiler_keys[(client_id, client_secret)] = await updateCodeAPICallLimits(client_id, client_secret)

    checkInstagramPost.start()
    givingUnassigned.start()
    checkingDualRoles.start()

    await syncMentorInformation()
    await remindUnassignedRoleMembers()


@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(CHANNEL_WELCOME)
    welcome_content = f'''Welcome {member.mention}!
Type `!h` whenever you need any help. Please carry out the following actions at the earliest:\n
1. Visit <#{CHANNEL_SELECTION_YEAR}> to select your batch year
2. Choose your campus at <#{CHANNEL_SELECTION_CAMPUS}>
3. Pick your favourite topics at <#{CHANNEL_SELECTION_TOPIC}>'''
    await welcome_channel.send(welcome_content)
    guild = bot.get_guild(GUILD_ID)
    unassign_role = discord.utils.get(guild.roles, id=ROLE_UNASSIGN)
    await member.add_roles(unassign_role)


@bot.event
async def on_command_error(ctx, error):
    content = "Invalid command.\nType `!help` for assistance with the bot or ping the `@Mod`s."
    await ctx.send(content)
    author = ctx.message.author
    content = f"{author.mention} made this error in {ctx.message.channel.mention}:\n{error}"
    channel = bot.get_channel(CHANNEL_BOT_TEST)
    await channel.send(content)


@bot.command(aliases=["syncmentors", "mentorsync"])
async def syncmentor(ctx):
    bot_dev_role = discord.utils.get(ctx.guild.roles, id=ROLE_BOT_DEV)
    if (bot_dev_role in ctx.author.roles):
        await syncMentorInformation()
        await ctx.send("Mentor information has been synced")
    else:
        await ctx.send(f"You are not authorised to run this command.")

@bot.command(aliases = ['lastsync'])
async def syncTime(ctx):
    await ctx.send(f"The mentor info was last synced <t:{MENTOR_SYNC_TIME}:R>")

@bot.command(aliases=['c'])
async def count(ctx, *roleName):
    roleName = ' '.join(roleName)
    try:
        roleName = roleName.split('&')
    except:
        pass

    roleName = [i.strip() for i in roleName]
    await ctx.send(f"Got request for role: {roleName}")

    if roleName == ['']:
        for guild in bot.guilds:
            await ctx.send(f"We have {len(guild.members)} people on this server!")
    else:
        thisRole = []
        for roles in roleName:
            thisRole.append(discord.utils.get(ctx.guild.roles, name=roles))
        for guild in bot.guilds:
            count = 0
            for member in guild.members:
                boolean = True
                for roles in thisRole:
                    if roles not in member.roles:
                        boolean = False
                if boolean:
                    count += 1
        await ctx.send(f"Number of members with {thisRole} role: {count}")


@bot.command(aliases=['purge'])
async def clear(ctx, amount=1):
    bot_dev_role = discord.utils.get(ctx.guild.roles, id=ROLE_BOT_DEV)
    if (bot_dev_role in ctx.author.roles):
        await ctx.channel.purge(limit=amount+1)
        await ctx.channel.send(f"Deleted {amount} messages")
        await asyncio.sleep(0.5)
        await ctx.channel.purge(limit=1)
    else:
        await ctx.channel.send(f"You do not have the required permissions to execute this command.")


@bot.command(aliases=["hi", "hello"])
async def greet(ctx):
    response = "Hello world, this is HackerSpace!"
    await ctx.send(response)


@bot.command()
async def ping(ctx):
    await ctx.send(f"Ping: {round(bot.latency * 1000)} ms")


@bot.command(aliases=['i'])
async def info(ctx):
    guild = bot.get_guild(GUILD_ID)
    await ctx.send(f'''I am in channel {ctx.message.channel.mention}
We have {len(guild.members)} people on this server!''')


@bot.command(aliases=["h", "help"])
async def assist(ctx):
    response = "DM or ping any of the `@Mod`s for more assistance"
    availableCommands = {
        'Ping Test': ['ping'],
        'Information on the server': ['i'],
        'Help': ['h', 'help'],
        'Count the number of people with a role': ['c', 'count'],
        'Look up a mentor for a topic': ['mentor {TOPIC NAME|MENTOR NAME}'],
        'Execute programming scripts': ['code']
    }

    embed = discord.Embed(
        title="Help",
        color=discord.Color.blue()
    )
    for help in availableCommands:
        commands = str()
        for command in availableCommands[help]:
            commands += f"`!{command}` - "
        embed.add_field(
            name="\u200b", value=f"{commands} {help}", inline=False)
    await ctx.send(response)
    await ctx.send(embed=embed)


async def getMentorResultEmbed(result):
    embed = discord.Embed(
        title="Mentor Lookup",
        color=discord.Color.blue()
    )
    for row in result:
        name = row["NAME"]
        discord_id = row["DISCORD ID"]
        email = row["EMAIL"]
        campus = row["CAMPUS"]
        domains = row["DOMAIN"].replace(',', ', ')
        member = bot.get_user(discord_id)

        content = f'''**Discord**: {member.mention}
**Email**: {email}
**Campus**: {campus} Campus
**Domains**: {domains}'''
        embed.add_field(
            name=name,
            value=content,
            inline=True
        )
    return embed


@bot.command(aliases=['mentors', 'Mentor'])
async def mentor(ctx, *, query=None):
    if query != None:
        queries = query.split('&')
        queries = list(map(str.strip, queries))
        result = getMentorResults(queries)
        if result:
            embed = await getMentorResultEmbed(result)
        else:
            possible_topics = "\n".join(list(MENTOR_DOMAIN_ACRONYMS.keys()))
            embed = discord.Embed(
                title="Mentor Lookup",
                description=f"No results found. Ping the `@Mod`s for additional help.\n\nHere are some available topics:\n{possible_topics}",
                color=discord.Color.blue()
            )
    else:
        embed = discord.Embed(
            title="Mentor Lookup",
            description="Please provide a query. Search for a mentor or a topic using `!mentor {TOPIC NAME | MENTOR NAME}`",
            color=discord.Color.blue()
        )
    await ctx.send(embed=embed)


@bot.command(aliases=['enableslash'])
async def flush_slash(ctx):
    CoreRR = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_RR)
    CoreEC = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_EC)
    Mod = discord.utils.get(ctx.guild.roles, id=ROLE_MOD)

    if((CoreRR in ctx.author.roles) or (CoreEC in ctx.author.roles) or (Mod in ctx.author.roles)):
        await ctx.channel.trigger_typing()
        await utils.manage_commands.remove_all_commands(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_ids=None)
        await utils.manage_commands.remove_all_commands(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_ids=[GUILD_ID])
        # await utils.manage_commands.add_slash_command(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_id=GUILD_ID, cmd_name='ask', description='Flourishes you with the pride of PESU', options=[create_option(name="msg_id", description="Message ID of any message you wanna reply to with the pride", option_type=3, required=False)])
        # await utils.manage_commands.add_slash_command(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_id=GUILD_ID, cmd_name='nickchange', description='Change someone else\'s nickname', options=[create_option(name="member", description="The member whose nickname you desire to change", option_type=6, required=True), create_option(name="new_name", description="The new name you want to give this fellow", option_type=3, required=True)])
        await utils.manage_commands.add_slash_command(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_id=GUILD_ID, cmd_name='ask', description='Ask an anonymous question', options=[create_option(name="Question", description="Question or general doubt that can be asked anonymously", option_type=3, required=True), create_option(name="msg_id", description="Message you want this question/answer to be a reply to", option_type=3, required=False)])
        await utils.manage_commands.add_slash_command(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_id=GUILD_ID, cmd_name='askban', description='Bans a user from submitting questions based on message ID', options=[create_option(name="msg_id", description="Message ID of the question", option_type=3, required=True)])
        await utils.manage_commands.add_slash_command(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_id=GUILD_ID, cmd_name='askbanuser', description="Bans a user from submitting questions", options=[create_option(name="member", description="User/Member to ban", option_type=6, required=True)])
        await utils.manage_commands.add_slash_command(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_id=GUILD_ID, cmd_name='askunbanuser', description="Unbans a user from submitting questions", options=[create_option(name="member", description="User/Member to unban", option_type=6, required=True)])
        await ctx.channel.send("Done")
        enabled = discord.Embed(title="Announcement from the mods", color=discord.Color.green(
        ), description="The ask features has been enabled")
        await bot.get_channel(864147401727410216).send(embed=enabled)
        overwrites = discord.PermissionOverwrite(view_channel=False)
        await bot.get_channel(864147401727410216).set_permissions(ctx.guild.default_role, overwrite=overwrites)
    else:
        await ctx.channel.send("You are not authorised for this")


@bot.command(aliases=['disableslash'])
async def disable_slash(ctx):
    CoreRR = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_RR)
    CoreEC = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_EC)
    Mod = discord.utils.get(ctx.guild.roles, id=ROLE_MOD)

    if((CoreRR in ctx.author.roles) or (CoreEC in ctx.author.roles) or (Mod in ctx.author.roles)):
        await ctx.channel.trigger_typing()
        await utils.manage_commands.remove_all_commands(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_ids=None)
        await utils.manage_commands.remove_all_commands(bot_id=BOT_ID, bot_token=BOT_TOKEN, guild_ids=[GUILD_ID])
        await ctx.channel.send("Done")
        disabled = discord.Embed(title="Announcement from the mods", color=discord.Color.red(
        ), description="The ask features has been disabled")
        await bot.get_channel(864147401727410216).send(embed=disabled)
        overwrites = discord.PermissionOverwrite(
            send_messages=False, view_channel=False)
        await bot.get_channel(864147401727410216).set_permissions(ctx.guild.default_role, overwrite=overwrites)
    else:
        await ctx.channel.send("You are not authorised for this")


async def storeId(memberId: str, messageId: str):
    global CONFESSIONS
    temp = CONFESSIONS
    # confessions = confessions
    for key in temp:
        if(key == memberId):
            temp[key].append(messageId)
            confessions = temp
            return
        else:
            continue
    CONFESSIONS[memberId] = [messageId]


@slash.slash(name="ask", description="Submits an anonymous questions", options=[create_option(name="Question", description="Question or general doubt that can be asked anonymously", option_type=3, required=True), create_option(name="msg_id", description="Message you want this question/answer to be a reply to", option_type=3, required=False)])
async def ask(ctx, *, question: str, msg_id: str = ''):
    await ctx.defer(hidden=True)
    banFile = open('data/ban_list.csv', 'r')
    memberId = str(ctx.author_id)
    banList = []
    title = "Anonymous Question"
    temp = msg_id
    try:
        msg_id = int(msg_id)
        title = "Anonymous reply"
    except:
        pass
    for line in banFile:
        banList.append(line.split('\n')[0].replace('\n', ''))
    if(memberId not in banList):
        confessEmbed = discord.Embed(title=title, color=discord.Color.random(
        ), description=question, timestamp=datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30))
        dest = bot.get_channel(864147401727410216)
        await ctx.send(f":white_check_mark: Your question has been submitted to {dest.mention}", hidden=True)
        try:
            msg_id = int(msg_id)
            msgObj = await dest.fetch_message(msg_id)
            await msgObj.reply(embed=confessEmbed)
        except:
            await dest.send(embed=confessEmbed)
        messages = await dest.history(limit=3).flatten()
        for message in messages:
            if((message.author.id == BOT_ID) and (len(message.embeds) > 0)):
                required_message = message
                break
        await storeId(str(ctx.author_id), str(required_message.id))
    else:
        await ctx.send(":x: You have been banned from submitting anonymous questions", hidden=True)


@slash.slash(name="askban", description='Bans a user from submitting questions based on message ID', options=[create_option(name="msg_id", description="Message ID of the question", option_type=3, required=True)])
async def askban(ctx, msg_id: str):
    CoreRR = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_RR)
    CoreEC = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_EC)
    Mod = discord.utils.get(ctx.guild.roles, id=ROLE_MOD)

    if((CoreRR in ctx.author.roles) or (CoreEC in ctx.author.roles) or (Mod in ctx.author.roles)):
        await ctx.defer(hidden=True)
        # global confessions
        # confessions = confessions
        msg_id_str = str(msg_id)
        banFile = open('data/ban_list.csv', 'r')
        banList = []
        for line in banFile:
            banList.append(line.split('\n')[0].replace('\n', ''))
        banFile.close()
        banFile = open('data/ban_list.csv', 'a')
        for key in CONFESSIONS:
            msgList = CONFESSIONS[key]
            if(msg_id_str in msgList):
                if(key not in banList):
                    banFile.write(f"{key}\n")
                    await ctx.send("Member banned succesfully", hidden=True)
                    banFile.close()
                    try:
                        dm = await bot.fetch_user(int(key))
                        dm_embed = discord.Embed(
                            title="Notification", description="You have been banned from submitting anonymous uestions", color=discord.Color.red())
                        await dm.send(embed=dm_embed)
                    except:
                        await ctx.send("DMs were closed", hidden=True)
                    return
                else:
                    await ctx.send("This fellow was already banned", hidden=True)
            else:
                continue
        await ctx.send("Could not ban", hidden=True)
        banFile.close()
    else:
        await ctx.send("You are not authorised to do this")


@slash.slash(name="askbanuser", description="Bans a user from submitting Questions", options=[create_option(name="member", description="User/Member to ban", option_type=6, required=True)])
async def askbanuser(ctx, member: discord.Member):
    CoreRR = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_RR)
    CoreEC = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_EC)
    Mod = discord.utils.get(ctx.guild.roles, id=ROLE_MOD)

    if((CoreRR in ctx.author.roles) or (CoreEC in ctx.author.roles) or (Mod in ctx.author.roles)):
        await ctx.defer(hidden=True)
        user_id = str(member.id)
        banFile = open('data/ban_list.csv', 'r')
        banList = []
        for line in banFile:
            banList.append(line.split('\n')[0].replace('\n', ''))
        banFile.close()
        if(user_id not in banList):
            banFile = open('data/ban_list.csv', 'a')
            banFile.write(f"{user_id}\n")
            await ctx.send("User banned succesfully", hidden=True)
            banFile.close()
            try:
                dm = await bot.fetch_user(int(user_id))
                dm_embed = discord.Embed(
                    title="Notification", description="You have been banned from submitting anonymous questions", color=discord.Color.red())
                await dm.send(embed=dm_embed)
            except:
                await ctx.send("DMs were closed", hidden=True)
        else:
            await ctx.send("This user has already been banned", hidden=True)
    else:
        await ctx.send("You are not authorised for this")


@cog_ext.cog_slash(name="askunbanuser", description="Unbans a user from submitting questions", options=[create_option(name="member", description="User/Member to unban", option_type=6, required=True)])
async def askunbanuser(ctx, member: discord.Member):
    CoreRR = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_RR)
    CoreEC = discord.utils.get(ctx.guild.roles, id=ROLE_CORE_EC)
    Mod = discord.utils.get(ctx.guild.roles, id=ROLE_MOD)

    if((CoreRR in ctx.author.roles) or (CoreEC in ctx.author.roles) or (Mod in ctx.author.roles)):
        await ctx.defer(hidden=True)
        user_id = str(member.id)
        dat = ''
        deleted = False
        banFile = open('data/ban_list.csv', 'r')
        for line in banFile:
            if(user_id in line.split(',')[0].replace('\n', '')):
                deleted = True
                continue
            dat += line
        banFile.close()
        if(deleted):
            banFile = open('data/ban_list.csv', 'w')
            banFile.write(dat)
            banFile.close()
            await ctx.send("User has been unbanned successfully", hidden=True)
            try:
                dm = await bot.fetch_user(int(user_id))

                dm_embed = discord.Embed(
                    title="Notification", description="You have been unbanned from submitting anonymous questions", color=discord.Color.green())
                await dm.send(embed=dm_embed)
            except:
                await ctx.send("DMs were closed", hidden=True)
        else:
            await ctx.send("This fellow was never banned in the first place", hidden=True)


@bot.command()
async def code(ctx, language, *, content=None):
    if language == "help":
        languages = ['ada', 'bash', 'bc', 'brainfuck', 'c', 'c-99', 'clisp', 'clojure', 'cobol', 'coffeescript',
                     'cpp', 'cpp17', 'csharp', 'd', 'dart', 'elixir', 'erlang', 'factor', 'falcon', 'fantom',
                     'forth', 'fortran', 'freebasic', 'fsharp', 'gccasm', 'go', 'groovy', 'hack', 'haskell',
                     'icon', 'intercal', 'java', 'jlang', 'kotlin', 'lolcode', 'lua', 'mozart', 'nasm', 'nemerle',
                     'nim', 'nodejs', 'objc', 'ocaml', 'octave', 'pascal', 'perl', 'php', 'picolisp', 'pike',
                     'prolog', 'python2', 'python3', 'r', 'racket', 'rhino', 'ruby', 'rust', 'scala', 'scheme',
                     'smalltalk', 'spidermonkey', 'sql', 'swift', 'tcl', 'unlambda', 'vbn', 'verilog',
                     'whitespace', 'yabasic']
        content = f'''`!code` uses the JDoodle code execution API which supports code compilation and execution for all major programming languages.

Supported languages: `{languages}`

To execute a script, use the following syntax for the command:

!code <language>
```
Enter code here, do not add syntax highlighting
```
<inputs for script>
'''
        await ctx.reply(content, mention_author=False)
    else:
        if content == None:
            await ctx.reply("Please enter a valid script. Use `!code help` to learn how to use the service.", mention_author=False)
        else:
            content = content.split("```")[1:]
            script, inputs = list(map(str.strip, content))
            if not inputs:
                inputs = None
            if not checkSpamCode(script, inputs):
                client_id, client_secret = max(
                    compiler_keys, key=lambda x: compiler_keys[x])
                try:
                    result = await executeCode(client_id, client_secret, script, language, inputs)
                    code_output = result.output.strip()
                    if not checkSpamCode(code_output):
                        if len(code_output) > 4000:
                            with open("output.txt", 'w') as f:
                                f.write(code_output)
                            await ctx.reply(f"Script took {result.cpuTime} seconds to execute and consumed {result.memory} kilobyte(s)", file=discord.File("output.txt"))
                            os.remove("output.txt")
                        else:
                            await ctx.reply(f"```\n{code_output}```\nScript took {result.cpuTime} seconds to execute and consumed {result.memory} kilobyte(s)", mention_author=False)
                    else:
                        await ctx.reply(f"No pinging `@everyone` or `@here` with the bot.")

                except Exception as error:
                    await ctx.reply(f"**Error occured**: {error}\n\nUse `!code help` to learn how to use the service.")

            else:
                await ctx.reply(f"No pinging `@everyone` or `@here` with the bot.")


async def getInstagramEmbed(username):
    html = getInstagramHTML(username)
    photo_time = getLastPhotoDate(html)
    post_embed = discord.Embed(
        title=f'Instagram Post from {username}', url=getPostLink(html), color=discord.Color.blue())
    if(checkVideo(html)):
        post_embed.set_image(url=getVideoURL(html))
    else:
        post_embed.set_image(url=getLastThumbnailURL(html))

    post_caption = getPhotoDescription(html)
    if post_caption != None:
        if len(post_caption) >= 1024:
            content_bodies = post_caption.split('\n')
            content_bodies = [c for c in content_bodies if c.strip() not in [
                "", " "]]
            for c in content_bodies:
                post_embed.add_field(name=f"\u200b", value=c, inline=False)
        else:
            post_embed.add_field(
                name="\u200b", value=post_caption, inline=False)
    post_embed.set_footer(text=datetime.datetime.fromtimestamp(photo_time))
    return post_embed, photo_time


@bot.command(aliases=["ig", "igpost"])
async def insta(ctx, username=None):
    if username == None:
        username = random.choice(["peshackerspace", "peshackerspace.ecc"])
    post_embed, _ = await getInstagramEmbed(username)
    await ctx.send(embed=post_embed)


@bot.command(aliases=["igrr", "igpostrr"])
async def instarr(ctx):
    username = "peshackerspace"
    post_embed, _ = await getInstagramEmbed(username)
    await ctx.send(embed=post_embed)


@bot.command(aliases=["igecc", "igpostecc"])
async def instaec(ctx):
    username = "peshackerspace.ecc"
    post_embed, _ = await getInstagramEmbed(username)
    await ctx.send(embed=post_embed)


@tasks.loop(minutes=5)
async def checkInstagramPost():
    await bot.wait_until_ready()
    instagram_usernames_channel = {
        "peshackerspace": CHANNEL_ANNOUNCEMENTS_RR,
        "peshackerspace.ecc": CHANNEL_ANNOUNCEMENTS_EC,
        "pes.spacejam": CHANNEL_ANNOUNCEMENTS
    }
    for username, channel_id in instagram_usernames_channel.items():
        try:
            post_embed, photo_time = await getInstagramEmbed(username)
            curr_time = time.time()
            if (curr_time - photo_time) <= 300:
                channel = bot.get_channel(channel_id)
                await channel.send(embed=post_embed)
                channel = bot.get_channel(CHANNEL_ANNOUNCEMENTS)
                await channel.send("@everyone", embed=post_embed)
        except Exception as error:
            print(f"Error while fetching Instagram post from {username}: {error}")
        await asyncio.sleep(1.5)


@tasks.loop(hours=12)
async def givingUnassigned():
    guild = bot.get_guild(GUILD_ID)
    unassign = discord.utils.get(guild.roles, id=ROLE_UNASSIGN)
    firstyear = discord.utils.get(guild.roles, id=ROLE_FIRSTYEAR)
    secondyear = discord.utils.get(guild.roles, id=ROLE_SECONDYEAR)
    thirdear = discord.utils.get(guild.roles, id=ROLE_THIRDYEAR)
    fourthyear = discord.utils.get(guild.roles, id=ROLE_FOURTHYEAR)
    grads = discord.utils.get(guild.roles, id=ROLE_GRAD)

    rrcampus = discord.utils.get(guild.roles, id=ROLE_CAMPUS_RR)
    eccampus = discord.utils.get(guild.roles, id=ROLE_CAMPUS_EC)
    outsiders = discord.utils.get(guild.roles, id=ROLE_CAMPUS_OUTSIDER)

    count = 0
    wrong_count = 0
    for member in guild.members:
        yeartaken = False
        campustaken = False
        if (firstyear in member.roles) or (secondyear in member.roles) or (thirdear in member.roles) or (fourthyear in member.roles) or (grads in member.roles):
            yeartaken = True
        if (eccampus in member.roles) or (rrcampus in member.roles) or (outsiders in member.roles):
            campustaken = True
        if yeartaken == False or campustaken == False:
            try:
                if not member.bot:
                    await member.add_roles(unassign)
                count += 1
            except Exception as error:
                wrong_count += 1

    channel = bot.get_channel(CHANNEL_BOT_TEST)
    await channel.send(f"Added unassigned for {count} and failed for {wrong_count}")


@tasks.loop(minutes=10)
async def checkingDualRoles():
    guild = bot.get_guild(GUILD_ID)
    unassign = discord.utils.get(guild.roles, id=ROLE_UNASSIGN)
    firstyear = discord.utils.get(guild.roles, id=ROLE_FIRSTYEAR)
    secondyear = discord.utils.get(guild.roles, id=ROLE_SECONDYEAR)
    thirdear = discord.utils.get(guild.roles, id=ROLE_THIRDYEAR)
    fourthyear = discord.utils.get(guild.roles, id=ROLE_FOURTHYEAR)
    grads = discord.utils.get(guild.roles, id=ROLE_GRAD)

    rrcampus = discord.utils.get(guild.roles, id=ROLE_CAMPUS_RR)
    eccampus = discord.utils.get(guild.roles, id=ROLE_CAMPUS_EC)
    outsiders = discord.utils.get(guild.roles, id=ROLE_CAMPUS_OUTSIDER)

    for member in guild.members:
        yeartaken = False
        campustaken = False
        if (unassign in member.roles):
            if (firstyear in member.roles) or (secondyear in member.roles) or (thirdear in member.roles) or (fourthyear in member.roles) or (grads in member.roles):
                yeartaken = True
            if (eccampus in member.roles) or (rrcampus in member.roles) or (outsiders in member.roles):
                campustaken = True
            if yeartaken and campustaken:
                await member.remove_roles(unassign)


bot.run(BOT_TOKEN)
