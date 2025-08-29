import discord
from discord.ext import commands, tasks
import json
import os
import logging
from datetime import datetime, timedelta

CANAL_EVENTOS_ID = INSERIR

class FormularioInscricao(discord.ui.Modal):
    def __init__(self, evento_nome):
        super().__init__(title=f"Inscrição: {evento_nome[:45]}")
        self.evento_nome = evento_nome
        
        self.add_item(discord.ui.InputText(label="Nome do seu Personagem", placeholder="Ex: Juliano Silva", required=True))
        self.add_item(discord.ui.InputText(label="ID do seu Personagem", placeholder="Ex: 1234", required=False))

    async def callback(self, interaction: discord.Interaction):
        nome_personagem = self.children[0].value
        id_personagem = self.children[1].value or "N/A"
        user_id = str(interaction.user.id)
        
        with open("events.json", "r+", encoding='utf-8') as f:
            eventos = json.load(f)
            if self.evento_nome in eventos:
                eventos[self.evento_nome]["participantes"][user_id] = {
                    "nome_personagem": nome_personagem,
                    "id_personagem": id_personagem
                }
                f.seek(0)
                json.dump(eventos, f, indent=4)
                f.truncate()
        
        await interaction.response.send_message("✅ **Sua inscrição foi confirmada com sucesso!**", ephemeral=True)

class ViewEvento(discord.ui.View):
    def __init__(self, evento_nome):
        super().__init__(timeout=None)
        self.evento_nome = evento_nome

    @discord.ui.button(label="Inscrever-se", style=discord.ButtonStyle.success, emoji="📝", custom_id="botao_inscrever_evento")
    async def inscrever(self, button: discord.ui.Button, interaction: discord.Interaction):
        evento_atual_nome = self.evento_nome
        
        with open("events.json", "r", encoding='utf-8') as f:
            eventos = json.load(f)
        
        if str(interaction.user.id) in eventos.get(evento_atual_nome, {}).get("participantes", {}):
            await interaction.response.send_message("⚠️ Você já está inscrito neste evento!", ephemeral=True)
            return
            
        modal = FormularioInscricao(evento_atual_nome)
        await interaction.response.send_modal(modal)

class Evento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger(__name__)
        self.persistent_views_added = False
        self.limpeza_eventos.start()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            eventos = self.load_data("events.json")
            for nome_evento, dados_evento in eventos.items():
                self.bot.add_view(ViewEvento(evento_nome=nome_evento), message_id=dados_evento["message_id"])

            self.persistent_views_added = True
            self.log.info("Views persistentes de eventos foram recarregadas.")

    def cog_unload(self):
        self.limpeza_eventos.cancel()

    @tasks.loop(hours=24)
    async def limpeza_eventos(self):
        self.log.info("Executando tarefa de limpeza de eventos antigos...")
        if not os.path.exists("events.json"): return
        try:
            with open("events.json", "r+", encoding='utf-8') as f:
                eventos = json.load(f)
                eventos_para_manter = {}
                trinta_dias_atras = datetime.now() - timedelta(days=30)
                for nome, dados in eventos.items():
                    criado_em = datetime.fromisoformat(dados["created_at"])
                    if criado_em > trinta_dias_atras:
                        eventos_para_manter[nome] = dados
                f.seek(0)
                json.dump(eventos_para_manter, f, indent=4)
                f.truncate()
            self.log.info("Limpeza de eventos concluída.")
        except Exception as e:
            self.log.error(f"Erro durante a limpeza de eventos: {e}", exc_info=True)

    @commands.slash_command(name="evento", description="Cria um novo evento com botão de inscrição.")
    @commands.has_permissions(administrator=True)
    async def evento(self, ctx, nome: str, data_hora: str, local: str):
        canal_alvo = self.bot.get_channel(CANAL_EVENTOS_ID)
        if not canal_alvo:
            await ctx.respond(f"❌ Erro: O canal de eventos com ID `{CANAL_EVENTOS_ID}` não foi encontrado.", ephemeral=True)
            return
        eventos = self.load_data("events.json")
        if nome in eventos:
            await ctx.respond(f"❌ Erro: Já existe um evento ativo com o nome '{nome}'. Escolha um nome único.", ephemeral=True)
            return
        embed = discord.Embed(title=f"🗓️ Novo Evento: {nome}", color=discord.Color.purple())
        embed.add_field(name="📅 Data e Hora", value=data_hora, inline=False)
        embed.add_field(name="📍 Local", value=local, inline=False)
        embed.set_footer(text=f"Evento criado por: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        view = ViewEvento(evento_nome=nome)
        try:
            mensagem_evento = await canal_alvo.send(content="@here", embed=embed, view=view)
            eventos[nome] = {
                "nome": nome, "data_hora": data_hora, "local": local,
                "message_id": mensagem_evento.id, "channel_id": canal_alvo.id,
                "created_at": datetime.now().isoformat(), "participantes": {}
            }
            self.save_data(eventos, "events.json")
            await ctx.respond(f"✅ Evento '{nome}' criado com sucesso no canal <#{CANAL_EVENTOS_ID}>!", ephemeral=False)
        except discord.Forbidden:
            await ctx.respond(f"❌ Erro: Não tenho permissão para enviar mensagens ou adicionar botões em <#{CANAL_EVENTOS_ID}>.", ephemeral=True)

    @commands.slash_command(name="inscritos", description="Exibe a lista de inscritos nos eventos ativos.")
    @commands.has_permissions(administrator=True)
    async def inscritos(self, ctx):
        eventos = self.load_data("events.json")
        if not eventos:
            await ctx.respond("Não há eventos ativos no momento.", ephemeral=True)
            return
        await ctx.defer(ephemeral=True)
        for nome_evento, dados_evento in eventos.items():
            embed = discord.Embed(title=f"Lista de Inscritos: {nome_evento}", color=discord.Color.from_rgb(114, 137, 218))
            participantes = dados_evento.get("participantes", {})
            if not participantes:
                embed.description = "Ainda não há ninguém inscrito neste evento."
            else:
                lista_inscritos = []
                for user_id, info in participantes.items():
                    try:
                        user_obj = await self.bot.fetch_user(int(user_id))
                        nome_discord = user_obj.mention
                    except discord.NotFound:
                        nome_discord = f"ID: {user_id} (Não encontrado)"
                    linha = (
                        f"**Usuário:** {nome_discord}\n"
                        f"**Personagem:** `{info['nome_personagem']}`\n"
                        f"**ID Personagem:** `{info['id_personagem']}`"
                    )
                    lista_inscritos.append(linha)
                embed.description = "\n\n".join(lista_inscritos)
            embed.set_footer(text=f"Total de inscritos: {len(participantes)}")
            await ctx.followup.send(embed=embed, ephemeral=True)

    def load_data(self, file_path):
        if not os.path.exists(file_path): return {}
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                content = f.read()
                return json.loads(content) if content else {}
        except (json.JSONDecodeError, FileNotFoundError): return {}

    def save_data(self, data, file_path):
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

def setup(bot):
    bot.add_cog(Evento(bot))