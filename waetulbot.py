import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=";")

@bot.event
async def on_ready():
    print("---연결 성공---")
    print(f"봇 이름 : {bot.user.name}")
    print(f"ID: {bot.user.id}")  
    await bot.change_presence(activity=discord.Game("명령어바뀜 ;help"))


initial_extensions = ['cogs.getproblem','cogs.ownercmd']


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bf = open("txtfile/bottoken.txt", "r")
bot_token = bf.readline()
bf.close()
bot.run(bot_token)

