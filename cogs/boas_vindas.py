import discord
from discord.ext import commands
import random
from datetime import datetime

CANAL_BOAS_VINDAS_NOME = "NOME REAL DO CANAL"

CANAL_REGRAS_ID = "INSERIR"

IMAGENS_BEMVINDO = [
    "https://i.imgur.com/vYd2d79.gif",
    "https://i.imgur.com/mC3JGeG.gif",
    "https://i.imgur.com/bWd1n3d.gif"
]

class BoasVindas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name=CANAL_BOAS_VINDAS_NOME)
        
        if channel is None:
            print(f"Aviso: Canal de boas-vindas '{CANAL_BOAS_VINDAS_NOME}' não encontrado.")
            return

        cor_aleatoria = random.randint(0, 0xFFFFFF)

        embed = discord.Embed(
            title=f"SEJA BEM-VINDO(A), NOVA LENDA!",
            description=(
                f"Olá **{member.name}**, que a sua jornada em **{member.guild.name}** seja épica!\n\n"
                f"Você é o **{member.guild.member_count}º** membro a se juntar à nossa comunidade. Contamos com você para torná-la ainda mais incrível.\n\n"
                f"› Não se esqueça de ler nossas diretrizes no canal <#{CANAL_REGRAS_ID}> para uma boa convivência.\n"
                f"› Apresente-se em um canal de chat e conheça nossa Família!"
            ),
            color=cor_aleatoria,
            timestamp=datetime.now()
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=random.choice(IMAGENS_BEMVINDO))
        embed.set_footer(text=f"ID do Usuário: {member.id}")
        
        try:
            await channel.send(content=f"👋 Boas-vindas ao nosso universo, {member.mention}!", embed=embed)
        except discord.Forbidden:
            print(f"Erro: O bot não tem permissão para enviar mensagens no canal '{CANAL_BOAS_VINDAS_NOME}'.")


def setup(bot):
    bot.add_cog(BoasVindas(bot))