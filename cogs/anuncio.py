import discord
from discord.ext import commands
import logging

CANAL_ANUNCIOS_ID = INSERIR

class Anuncio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger(__name__)

    @commands.slash_command(name="anunciar", description="Envia um anúncio oficial como um embed em um canal específico.")
    @commands.has_permissions(administrator=True)
    async def anunciar(self, ctx, titulo: str, mensagem: str):
        
        canal_alvo = self.bot.get_channel(CANAL_ANUNCIOS_ID)
        
        if not canal_alvo:
            await ctx.respond(f"❌ Erro: O canal de anúncios com ID `{CANAL_ANUNCIOS_ID}` não foi encontrado.", ephemeral=True)
            self.log.error(f"Canal de anúncios com ID {CANAL_ANUNCIOS_ID} não encontrado.")
            return

        embed = discord.Embed(
            title=f"📢 {titulo}",
            description=mensagem,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Anúncio por: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        try:
            await canal_alvo.send(content="@here", embed=embed)
            await ctx.respond("✅ Anúncio enviado com sucesso!", ephemeral=False)
            self.log.info(f"'{ctx.author.name}' criou um anúncio com título '{titulo}'.")
        except discord.Forbidden:
            await ctx.respond(f"❌ Erro: Não tenho permissão para enviar mensagens no canal <#{CANAL_ANUNCIOS_ID}>.", ephemeral=True)
            self.log.error(f"Sem permissão para enviar mensagem no canal de anúncios {CANAL_ANUNCIOS_ID}.")

    @anunciar.error
    async def anunciar_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("❌ Você não tem permissão de administrador para usar este comando!", ephemeral=True)
        else:
            self.log.error(f"Erro no comando /anunciar: {error}", exc_info=True)
            await ctx.respond("❌ Ocorreu um erro inesperado.", ephemeral=True)


def setup(bot):
    bot.add_cog(Anuncio(bot))