import discord
import datetime
from discord.ext import commands
import asyncio


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except:
            await ctx.send("리로드 실패")
            return
        await ctx.send("리로드 완료")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        try:
            self.bot.load_extension(cog)
        except:
            await ctx.send("로드 실패")
            return
        await ctx.send("로드 완료")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        try:
            self.bot.unload_extension(cog)
        except:
            await ctx.send("언로드 실패")
            return
        await ctx.send("언로드 완료")

def setup(bot):
    bot.add_cog(Admin(bot))
    print("패치기능 로드")