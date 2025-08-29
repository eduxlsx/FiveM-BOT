import discord
from discord.ext import commands
import random

CITacoes = [
    "Acredite em você mesmo e tudo será possível.",
    "O sucesso é a soma de pequenos esforços repetidos dia após dia.",
    "A persistência realiza o impossível.",
]

class Motivacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="motivar", description="Receba uma citação motivacional!")
    async def motivar(self, ctx):
        citacao_escolhida = random.choice(CITacoes)
        await ctx.respond(f'💡 {citacao_escolhida}')

def setup(bot):
    bot.add_cog(Motivacao(bot))