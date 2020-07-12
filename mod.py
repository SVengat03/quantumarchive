from typing import Union

from discord.ext import commands
import discord
import inspect
import re
import io
import contextlib
import traceback
import urllib.request
import urllib.parse
import math
import random
import time
import datetime

from dbwrapper import DB
from paginator import *
from simplepaginator import SimplePaginator
from quantumutils import *

class Mod(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self,ctx,user:discord.Member,*,reason=None):
        '''Kicks members from the server'''
        if reason is None:
            await ctx.send(ctx.author.mention+", please give your reason.",delete_after=20)
            def check(message):
                return message.author==ctx.author and message.channel==ctx.channel
            try:
                message = await self.bot.wait_for("message",check=check,timeout=20)
                if message.content.lower()=="no":
                    raise asyncio.TimeoutError
                reason = message.content
            except asyncio.TimeoutError:
                await ctx.send("No reason has been specified")
                reason = "<Not specified>"
        embed = discord.Embed(title="Member kicked",colour=discord.Colour.dark_gold())
        embed.add_field(name="Name",value=user.display_name)
        embed.add_field(name="Reason",value=reason)
        embed.add_field(name="Done by",value=ctx.author.mention)
        await ctx.guild.kick(user,reason=reason)
        await ctx.send(embed=embed)
        await ctx.guild.get_channel(559940242455658497).send(embed=embed)
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        '''The mighty ban hammer'''
        if reason is None:
            await ctx.send(ctx.author.mention + ", please give your reason.",delete_after=20)

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel

            try:
                message = await self.bot.wait_for("message", check=check, timeout=20)
                if message.content.lower() == "no":
                    raise asyncio.TimeoutError
                reason = message.content
            except asyncio.TimeoutError:
                await ctx.send("No reason has been specified")
                reason = "<Not specified>"
        embed = discord.Embed(title="Member banned", colour=discord.Colour.dark_gold())
        embed.add_field(name="Name", value=user.display_name)
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Done by",value=ctx.author.mention)
        await ctx.guild.ban(user,reason=reason)
        await ctx.send(embed=embed)
        await ctx.guild.get_channel(559940242455658497).send(embed=embed)
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, id):
        '''unbans users, if you have ban_members perms'''
        if not id.isnumeric():
            await ctx.send("Please give the user's id as a parameter!")
            return
        iid = int(id)
        if iid not in [i.user.id for i in (await ctx.guild.bans())]:
            await ctx.send("This user is not currently banned!")
            return
        user = await self.bot.fetch_user(iid)
        embed = discord.Embed(title="User unbanned", colour=discord.Colour.dark_gold())
        embed.add_field(name="Name", value=user.name+"#"+str(user.discriminator))
        embed.add_field(name="Done by",value=ctx.author.mention)
        await ctx.guild.unban(user)
        await ctx.send(embed=embed)
        await ctx.guild.get_channel(559940242455658497).send(embed=embed)
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        '''Mutes users if you have kick_member perms'''
        if reason is None:
            await ctx.send(ctx.author.mention + ", please give your reason.",delete_after=20)

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel

            try:
                message = await self.bot.wait_for("message", check=check, timeout=20)
                if message.content.lower() == "no":
                    raise asyncio.TimeoutError
                reason = message.content
            except asyncio.TimeoutError:
                await ctx.send("No reason has been specified")
                reason = "<Not specified>"
        embed = discord.Embed(title="Member muted", colour=discord.Colour.dark_gold())
        embed.add_field(name="Name", value=user.display_name)
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Done by",value=ctx.author.mention)
        await user.add_roles(ctx.guild.get_role(694870418024169535))
        await ctx.send(embed=embed)
        await ctx.guild.get_channel(559940242455658497).send(embed=embed)
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, *, user:discord.Member):
        '''helps to mute already-muted members'''
        if user not in ctx.guild.get_role(694870418024169535).members:
            await ctx.send("This user was not muted!")
        embed = discord.Embed(title="User unmuted", colour=discord.Colour.dark_gold())
        embed.add_field(name="Name", value=user.display_name)
        embed.add_field(name="Done by",value=ctx.author.mention)
        await user.remove_roles(ctx.guild.get_role(694870418024169535))
        await ctx.send(embed=embed)
        await ctx.guild.get_channel(559940242455658497).send(embed=embed)
        await ctx.message.add_reaction("✅")

    @commands.check(important)
    @commands.command()
    async def announce(self,ctx,*,message=None):
        '''Lets Praetors and Consuls announce, as well as the bot owner. Ping server announcements by adding ' ping' at the end.'''
        if message==None:
            await ctx.send("Please include a message!",delete_after=5)
            return
        ping = False
        if message[-5:]==" ping":
            ping = True
            message = message[:-5]
        if commands.is_owner():
            #bot announcement
            embed = discord.Embed(title="Bot update!",
                                  description=message,
                                  colour=discord.Colour.dark_gold())
            embed.set_footer(text="Announcement from Napoleon Bonaparte#9043", icon_url=str(ctx.author.avatar_url))
            m = await ctx.send("Proceed with announcement?",embed=embed)
            try:
                for i in "✅❌":
                    await m.add_reaction(i)
                confirm = await self.bot.wait_for("reaction_add",check=lambda r,m:r.emoji in "✅❌" and m.id==ctx.author.id,timeout=10)
                if confirm[0].emoji=="❌":
                    raise asyncio.TimeoutError
                elif confirm[0].emoji=="✅":
                    if ping:
                        await ctx.guild.get_channel(559944766549262356).send("<@&689808478717345866>",embed=embed)
                    else:
                        await ctx.guild.get_channel(559944766549262356).send(embed=embed)
            except asyncio.TimeoutError:
                await ctx.send("Announcement was cancelled.",delete_after=5)
                await m.delete()
        else:
            #server announcement
            embed = discord.Embed(title="Server update!",
                                  description=message,
                                  colour=ctx.author.colour)
            embed.set_footer(text=f"Announcement from {ctx.author.name}#{ctx.author.discriminator}", icon_url=str(ctx.author.avatar_url))
            m = await ctx.send("Proceed with announcement?", embed=embed)
            try:
                for i in "✅❌":
                    await m.add_reaction(i)
                confirm = await self.bot.wait_for("reaction_add", check=lambda r, m: r.emoji in "✅❌", timeout=10)
                if confirm[0].emoji == "❌":
                    raise asyncio.TimeoutError
                elif confirm[0].emoji == "✅":
                    if ping:
                        await ctx.guild.get_channel(559944766549262356).send("<@&689808478717345866>", embed=embed)
                    else:
                        await ctx.guild.get_channel(559944766549262356).send(embed=embed)
            except asyncio.TimeoutError:
                await ctx.send("Announcement was cancelled.", delete_after=5)
                await m.delete()

    @commands.check(important)
    @commands.group()
    async def autorole(self,ctx):
        '''Returns list of autoroles, "add" adds new ones and "remove" removes autoroles'''
        if ctx.invoked_subcommand is not None:
            return
        async with ctx.typing():
            dab = DB("AutoRoles")
            dab.set_collection("roles")
            rolelist = await dab.find()
            embed=discord.Embed(title="List of all autoroles",colour=ctx.author.colour)
            embed.description = "\n".join(i["emoji"]+": "+ctx.guild.get_role(i["roleid"]).mention for i in rolelist)
        await ctx.send(embed=embed)

    @commands.check(important)
    @autorole.command()
    async def add(self,ctx,emoji:Union[discord.Emoji,str],*,rolename):
        '''Add new autoroles'''
        role = list(filter(lambda x:x.name==rolename,ctx.guild.roles))
        if not role:
            await ctx.send(f"{ctx.author.mention}, the role specified doesn't exist. Try again, character for character.")
            return
        role = role[0]
        def oo(m):
            return m.author.id==ctx.author.id and m.channel.id == ctx.channel.id
        await ctx.send(f"{ctx.author.mention}, please add a description.",delete_after=40)
        try:
            desc = await self.bot.wait_for("message",timeout=40,check=oo)
        except asyncio.TimeoutError:
            await ctx.send("Autorole assignment failed. Try again.",delete_after=5)
            return
        async with ctx.typing():
            db = DB("AutoRoles")
            db.set_collection("roles")
            await db.insertnorepeat(emoji=emoji,roleid=role.id)
        await ctx.send(embed=discord.Embed(title="Add autorole",description=emoji+" "+role.mention,colour=ctx.author.colour))
        mess = await ctx.guild.get_channel(709028380850389043).fetch_message(731853316383965194)
        emb = mess.embeds[0]
        emb.add_field(name=str(emoji)+" "+role.name.title(),value=desc.content)
        await mess.add_reaction(emoji)
        await mess.edit(embed=emb)

    @commands.check(important)
    @autorole.command()
    async def remove(self, ctx, emoji:Union[discord.Emoji,str], *, rolename):
        '''Add new autoroles'''
        role = list(filter(lambda x: x.name == rolename, ctx.guild.roles))
        if not role:
            await ctx.send(
                f"{ctx.author.mention}, the role specified doesn't exist. Try again, character for character.")
            return
        role = role[0]
        async with ctx.typing():
            db = DB("AutoRoles")
            db.set_collection("roles")
            await db.delete(emoji=emoji, roleid=role.id)
        await ctx.send(embed=discord.Embed(title="Remove autorole", description=emoji + " " + role.mention,
                                           colour=ctx.author.colour))
        mess = await ctx.guild.get_channel(709028380850389043).fetch_message(731853316383965194)
        emb = mess.embeds[0]
        emb.remove_field(list(i.name for i in emb.fields).index(emoji+" "+role.name.title()))
        await mess.clear_reaction(emoji)
        await mess.edit(embed=emb)

def setup(bot):
    bot.add_cog(Mod(bot))