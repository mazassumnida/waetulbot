import os
import discord
from discord.ext import commands
import requests
import datetime 
from dateutil import tz
import chardet

boj_api_server_user = os.environ["boj_user"]
boj_api_server_search = os.environ["boj_problem"]

with open(r"txtfile/boj_levels.txt", "r") as f_L:
    boj_levels = f_L.readlines()

with open(r"txtfile/boj_colors.txt", "r") as f_L:
    boj_colors = f_L.readlines()

with open(r"txtfile/cf_ranks.txt", "r") as f_L:
    cf_ranks = f_L.readlines()

with open(r"txtfile/cf_colors.txt", "r") as f_L:
    cf_colors = f_L.readlines()

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('Asia/Seoul')


def boj_calcul100(json):
    next_exp = json['next_exp_cap']
    prev_exp = json['previous_exp_cap']
    exp_gap = next_exp - prev_exp
    my_exp = json['exp']
    p = round((my_exp - prev_exp) * 100 / exp_gap)
    return format(my_exp - prev_exp, ','), format(exp_gap, ','), p


def boj_colorselect(lv):
    if lv == 0:
        return 0x010101
    if lv == 31:
        return 0x010101
    return int(boj_colors[(lv-1)//5], 0)


def boj_rating_to_lv(rating):
    if rating < 30: return 0
    if rating < 150: return rating // 30
    if rating < 200: return 5
    if rating < 500: return (rating-200) // 100 + 6
    if rating < 1400: return (rating-500) // 150 + 9
    if rating < 1600: return 15
    if rating < 1750: return 16
    if rating < 1900: return 17
    if rating < 2800: return (rating-1900) // 100 + 18
    if rating < 3000: return (rating-2800) // 50 + 27
    return 31

def boj_class_deco(deco):
    if deco == "gold":return 2
    elif deco == "silver": return 1
    return 0



def cf_dateconvert(s):
    return datetime.datetime.utcfromtimestamp(s).replace(tzinfo=from_zone).astimezone(to_zone)


def cf_rankselect(rating):
    if rating < 1200:
        return cf_ranks[0]
    if rating < 1400:
        return cf_ranks[1]
    if rating < 1600:
        return cf_ranks[2]
    if rating < 1900:
        return cf_ranks[3]
    if rating < 2100:
        return cf_ranks[4]
    if rating < 2300:
        return cf_ranks[5]
    if rating < 2400:
        return cf_ranks[6]
    if rating < 2600:
        return cf_ranks[7]
    if rating < 3000:
        return cf_ranks[8]
    return cf_ranks[9]


def cf_colorselect(rating):
    if rating < 1200:
        return int(cf_colors[0], 0)
    if rating < 1400:
        return int(cf_colors[1], 0)
    if rating < 1600:
        return int(cf_colors[2], 0)
    if rating < 1900:
        return int(cf_colors[3], 0)
    if rating < 2100:
        return int(cf_colors[4], 0)
    if rating < 2600:
        return int(cf_colors[5], 0)
    if rating < 3000:
        return int(cf_colors[6], 0)
    return int(cf_colors[7], 0)


class numcog(commands.Cog, name="numCommanding"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["bu", "BU", "ㅠㅕ", "buser", "boj", "BOJ", "ㅠㅐㅓ"])
    async def 백준유저검색(self, ctx, *informations):
        """;boj 백준핸들"""
        for info in informations:
            user_info = requests.get(boj_api_server_user + info).json()
            lv = boj_rating_to_lv(user_info["rating"])
            em = discord.Embed(title=info, color=boj_colorselect(lv), url="https://solved.ac/profile/" + info)
            em.set_thumbnail(url=boj_levels[lv])
            em.add_field(name="**solved**", value=user_info["solvedCount"], inline=1)
            em.add_field(name="**AC rating**", value= user_info["rating"], inline=1)
            em.add_field(name="**class**", value= f"{user_info['class']}{'+'*boj_class_deco(user_info['classDecoration'])}", inline=1)
            await ctx.send(embed=em)
    
    @commands.command(aliases=["s","S","ㄴ","search"])
    async def 백준문제검색(self, ctx, *informations):
        """;s 백준문제이름"""
        server_search = boj_api_server_search
        for information in informations:
            server_search += f" {information}"
        search_result = requests.get(server_search).json()["items"]
        for pro in search_result[:3]:
            em = discord.Embed(title = f"pro['problemId']번: pro['titleKo']", color=boj_colorselect(pro["level"]),
                               url="https://www.acmicpc.net/problem/"+pro['problemId'])
            em.set_thumbnail(url=boj_levels[pro["level"]])
            em.add_field(name="solved", value= pro['acceptedUserCount'], inline=1)
            em.add_field(name="average try", value="%0.2f" % pro['averageTries'], inline=1)
            await ctx.send(embed=em)
    @commands.command(aliases=["c", "C", "ㅊ", "contest"])
    async def 코포컨테스트(self, ctx):
        """;contest"""
        em = discord.Embed(title="Contest List", color=0, url=r"https://codeforces.com/contests")
        now = datetime.datetime.utcnow().replace(tzinfo=from_zone).astimezone(to_zone)
        L = []
        playing = []
        wating = []
        em.set_thumbnail(url="https://play-lh.googleusercontent.com/WQNrSO2ottLarqVtfEjZdEuZglZTytNdddm6pvMtSwSW_StRCkgd9-BRp6kS_JApdbA")
        for i in requests.get(r'https://codeforces.com/api/contest.list?gym=false').json()["result"]:
            if i["phase"] == "FINISHED":
                break
            if i["phase"] == "CODING":
                playing.append(i)
            elif chardet.detect(i["name"].encode())["encoding"] != 'utf-8':
                if i["relativeTimeSeconds"] >= -86400:
                    wating.append(i)
                else:
                    L.append(i)
        for i in playing:
            playingtime = datetime.timedelta(seconds = i["relativeTimeSeconds"])
            differ = f"시작한지 {playingtime.days}일 {playingtime.seconds//3600}시간 {(playingtime.seconds%3600)//60}분 " \
                     f"{(playingtime.seconds%3600)%60}초 지남"
            em.add_field(name=i["name"],
                         value=f"진행중!\n{differ}\n[register](https://codeforces.com/contestRegistration/{i['id']})",
                         inline=0)
        for i in wating[::-1]:
            date = cf_dateconvert(i["startTimeSeconds"])
            rink = f"https://www.timeanddate.com/worldclock/fixedtime.html?day={date.day}&month={date.month}" \
                   f"&year={date.year}&hour=16&min={date.minute}&sec={date.second}&p1=166"
            dif = date - now
            differ = f"{dif.days}일 {dif.seconds//3600}시간 {(dif.seconds%3600)//60}분 {(dif.seconds%3600)%60}초 뒤 시작"
            em.add_field(name=i["name"], value = f"[register!](https://codeforces.com/contestRegistration/{i['id']})\n[{date}\n{differ}]({rink})", inline= 0)
        for i in L[::-1]:
            date = cf_dateconvert(i["startTimeSeconds"])
            rink = f"https://www.timeanddate.com/worldclock/fixedtime.html?day={date.day}&month={date.month}" \
                   f"&year={date.year}&hour=16&min={date.minute}&sec={date.second}&p1=166"
            dif = date - now
            differ = f"{dif.days}일 {dif.seconds//3600}시간 {(dif.seconds%3600)//60}분 {(dif.seconds%3600)%60}초 뒤 시작"
            em.add_field(name=i["name"], value = f"[{date}\n{differ}]({rink})", inline= 0)
        await ctx.send(embed=em)
    @commands.command(aliases=["cu", "CU", "쳐", "cuser", "CF", "ㅊㄹ", "cf"])
    async def 코포유저검색(self, ctx, handle):
        """;cf 코포핸들"""
        user_info = requests.get(f'https://codeforces.com/api/user.info?handles={handle}').json()["result"][0]
        em = discord.Embed(title = handle,
                           color = cf_colorselect(user_info["rating"]),
                           url = "https://codeforces.com/profile/"+handle)
        em.set_thumbnail(url=cf_rankselect(user_info["rating"]))
        em.add_field(name="**Rating**", value= f'**{user_info["rating"]}**\n*{user_info["rank"]}*', inline=1)
        em.add_field(name="**TopRating**", value= f'**{user_info["maxRating"]}**\n*{user_info["maxRank"]}*', inline=1)
        cinfo = requests.get(f'https://codeforces.com/api/user.rating?handle={handle}').json()["result"][-1]
        if cinfo['newRating'] - cinfo['oldRating'] >= 0:
            em.add_field(name="**recent contest**",
                         value = f"*{cinfo['contestName']}* \nrating : {cinfo['oldRating']} -> {cinfo['newRating']}(+{cinfo['newRating'] - cinfo['oldRating']})\nrank : {cinfo['rank']}",
                         inline=0)
        else:
            em.add_field(name="**recent contest**",
                         value = f"*{cinfo['contestName']}* \nrating : {cinfo['oldRating']} -> {cinfo['newRating']}({cinfo['newRating'] - cinfo['oldRating']})\nrank : {cinfo['rank']}",
                         inline=0)
        await ctx.send(embed=em)


'''
아니 개어려웡임 아라ㅏ니인이
'''


def setup(bot):
    bot.add_cog(numcog(bot))
    print("문제명령어 로드")
