import discord
from discord.ext import commands
import random

EMOJIS_INCENTIVADORES = ["👍", "🎉", "🔥", "💯", "⭐", "🚀", "🙌", "✅", "✨"]
CHANCE_DE_REAGIR = 0.2

class Reacoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if random.random() < CHANCE_DE_REAGIR:
            emoji_escolhido = random.choice(EMOJIS_INCENTIVADORES)
            try:
                await message.add_reaction(emoji_escolhido)
            except Exception as e:
                print(f"Não foi possível reagir: {e}")

def setup(bot):
    bot.add_cog(Reacoes(bot))