import discord
from discord.ext import commands
import json
import os
import logging
from datetime import datetime

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = "warnings.json"
        self.log_file = "action_logs.json"
        self.log = logging.getLogger(__name__)
        self.adv_roles = {
            1: ADV1,
            2: ADV2,
            3: ADV3,
        }

    def load_data(self, file_path):
        if not os.path.exists(file_path):
            return {} if file_path == self.warnings_file else []
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                content = f.read()
                if not content:
                    return {} if file_path == self.warnings_file else []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return {} if file_path == self.warnings_file else []

    def save_data(self, data, file_path):
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    async def _log_action(self, action, admin, target, reason):
        logs = self.load_data(self.log_file)
        new_log = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "action": action,
            "admin_id": str(admin.id),
            "admin_name": admin.name,
            "target_id": str(target.id),
            "target_name": target.name,
            "reason": reason
        }
        logs.append(new_log)
        self.save_data(logs, self.log_file)

    async def _update_adv_roles(self, membro, total_warnings):
        guild = membro.guild
        current_roles_to_remove = [guild.get_role(role_id) for role_id in self.adv_roles.values() if guild.get_role(role_id) in membro.roles]
        if current_roles_to_remove:
            await membro.remove_roles(*current_roles_to_remove, reason="Atualização de cargos de advertência.")
        
        if total_warnings in self.adv_roles:
            new_role_id = self.adv_roles[total_warnings]
            new_role = guild.get_role(new_role_id)
            if new_role:
                await membro.add_roles(new_role, reason=f"Recebeu {total_warnings}ª advertência.")

    @commands.slash_command(name="advertir", description="Adverte um membro, registra o aviso e atribui o cargo.")
    @commands.has_permissions(moderate_members=True)
    async def advertir(self, ctx, membro: discord.Member, *, motivo: str):
        if membro.bot or membro == ctx.author:
            await ctx.respond("Você não pode advertir a si mesmo ou a um bot!", ephemeral=True)
            return
        if membro.top_role >= ctx.author.top_role:
             await ctx.respond("Você não pode advertir um membro com cargo igual ou superior ao seu.", ephemeral=True)
             return

        warnings = self.load_data(self.warnings_file)
        member_id = str(membro.id)

        if member_id not in warnings:
            warnings[member_id] = []
        
        new_warning = {
            "motivo": motivo,
            "admin_id": str(ctx.author.id),
            "admin_nome": ctx.author.name
        }
        warnings[member_id].append(new_warning)
        self.save_data(warnings, self.warnings_file)
        
        await self._log_action("WARN", ctx.author, membro, motivo)
        
        total_warnings = len(warnings[member_id])
        await self._update_adv_roles(membro, total_warnings)
        
        self.log.info(f"'{ctx.author.name}' advertiu '{membro.name}'. Motivo: {motivo}. Total: {total_warnings}")

        try:
            await membro.send(f"🚨 Você foi advertido no servidor '{ctx.guild.name}' por {ctx.author.mention}!\n**Motivo:** {motivo}\n**Total de advertências:** {total_warnings}/4")
        except discord.Forbidden:
            self.log.warning(f"Não foi possível enviar a DM de advertência para {membro.name}.")

        await ctx.respond(f"✅ {membro.mention} foi advertido e seu cargo foi atualizado. Total de advertências: **{total_warnings}**.", ephemeral=False)

        if total_warnings >= 4:
            self.log.warning(f"BAN AUTOMÁTICO: '{membro.name}' atingiu 4 advertências.")
            try:
                warnings.pop(member_id, None)
                self.save_data(warnings, self.warnings_file)
                await self._log_action("AUTO-BAN", self.bot.user, membro, f"Atingiu 4 advertências. Última por {ctx.author.name}: {motivo}")
                await membro.ban(reason=f"Banido automaticamente por atingir 4 advertências. Última por {ctx.author.name}: {motivo}")
                await ctx.channel.send(f"🔥 **{membro.mention} foi banido automaticamente** por atingir 4 advertências!")
            except discord.Forbidden:
                self.log.error(f"FALHA AO BANIR: Não tenho permissão para banir {membro.name}.")

    @commands.slash_command(name="removeradv", description="Remove uma advertência de um membro e ajusta o cargo.")
    @commands.has_permissions(moderate_members=True)
    async def removeradv(self, ctx, membro: discord.Member, numero: int, *, motivo_revogacao: str):
        warnings = self.load_data(self.warnings_file)
        member_id = str(membro.id)

        if member_id not in warnings or not warnings[member_id]:
            await ctx.respond(f"{membro.mention} não possui advertências para remover.", ephemeral=True)
            return

        if not (1 <= numero <= len(warnings[member_id])):
            await ctx.respond(f"Número de advertência inválido. Use `/veravisos`.", ephemeral=True)
            return

        removed_warning = warnings[member_id].pop(numero - 1)
        self.save_data(warnings, self.warnings_file)
        
        await self._log_action("UNWARN", ctx.author, membro, f"Advertência '{removed_warning['motivo']}' removida. Razão: {motivo_revogacao}")

        total_warnings = len(warnings.get(member_id, []))
        await self._update_adv_roles(membro, total_warnings)

        self.log.info(f"'{ctx.author.name}' revogou a advertência #{numero} de '{membro.name}'.")
        
        try:
            await membro.send(f"✅ Uma de suas advertências no servidor '{ctx.guild.name}' foi revogada por {ctx.author.mention}.\n**Motivo:** {motivo_revogacao}")
        except discord.Forbidden:
            pass

        await ctx.respond(f"✅ Advertência #{numero} de {membro.mention} removida e cargo ajustado. Total agora: **{total_warnings}**.", ephemeral=False)

    logs_group = discord.SlashCommandGroup("logs", "Comandos para visualizar logs de moderação")

    @logs_group.command(name="advertencias", description="Mostra o histórico de advertências de um membro.")
    @commands.has_permissions(moderate_members=True)
    async def logs_advertencias(self, ctx, membro: discord.Member):
        action_logs = self.load_data(self.log_file)
        member_id = str(membro.id)
        user_warn_logs = [log for log in action_logs if log.get("target_id") == member_id and log.get("action") in ["WARN", "UNWARN"]]

        if not user_warn_logs:
            await ctx.respond(f"{membro.mention} não possui histórico de advertências.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Histórico de Advertências de {membro.name}", color=discord.Color.blue())
        description = ""
        for log in user_warn_logs:
            action_emote = "➕" if log['action'] == 'WARN' else "➖"
            description += f"**{action_emote} {log['action']}** em `{log['timestamp']}`\n"
            description += f"**Admin:** {log['admin_name']}\n"
            description += f"**Motivo:** {log['reason']}\n---\n"
        
        embed.description = description[:4096]
        await ctx.respond(embed=embed, ephemeral=False)

    @logs_group.command(name="bans", description="Mostra o histórico de bans de um membro.")
    @commands.has_permissions(ban_members=True)
    async def logs_bans(self, ctx, membro: discord.User):
        action_logs = self.load_data(self.log_file)
        member_id = str(membro.id)
        user_ban_logs = [log for log in action_logs if log.get("target_id") == member_id and "BAN" in log.get("action")]

        if not user_ban_logs:
            await ctx.respond(f"{membro.mention} não possui histórico de banimentos.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Histórico de Bans de {membro.name}", color=discord.Color.red())
        description = ""
        for log in user_ban_logs:
            description += f"**💥 {log['action']}** em `{log['timestamp']}`\n"
            description += f"**Admin:** {log['admin_name']}\n"
            description += f"**Motivo:** {log['reason']}\n---\n"
            
        embed.description = description[:4096]
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name="veravisos", description="Mostra as advertências ativas de um membro.")
    @commands.has_permissions(moderate_members=True)
    async def veravisos(self, ctx, membro: discord.Member):
        warnings = self.load_data(self.warnings_file)
        member_id = str(membro.id)
        if member_id not in warnings or not warnings[member_id]:
            await ctx.respond(f"{membro.mention} não possui advertências ativas.", ephemeral=True)
            return
        user_warnings = warnings[member_id]
        embed = discord.Embed(title=f"Advertências Ativas de {membro.name}", color=discord.Color.orange(), description=f"Total: {len(user_warnings)}")
        for i, warn in enumerate(user_warnings, 1):
            admin_user = warn.get("admin_nome", "Desconhecido")
            embed.add_field(name=f"Advertência #{i}", value=f"**Motivo:** {warn['motivo']}\n**Aplicada por:** {admin_user}", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
        
    @commands.slash_command(name="banir", description="Bane um membro do servidor.")
    @commands.has_permissions(ban_members=True)
    async def banir(self, ctx, membro: discord.Member, *, motivo: str):
        if membro == ctx.author:
            await ctx.respond("Você não pode se banir!", ephemeral=True)
            return
        if membro.top_role >= ctx.author.top_role:
             await ctx.respond("Você não pode banir um membro com cargo igual ou superior ao seu.", ephemeral=True)
             return
            
        try:
            await self._log_action("BAN", ctx.author, membro, motivo)
            await membro.ban(reason=f"Banido por {ctx.author.name}. Motivo: {motivo}")
            await ctx.respond(f"✅ {membro.mention} foi banido com sucesso. Motivo: {motivo}")
        except discord.Forbidden:
            self.log.error(f"FALHA AO BANIR: O bot não tem permissão para banir {membro.name}.")
            await ctx.respond("❌ Eu não tenho permissão para banir este membro!", ephemeral=True)

    @commands.slash_command(name="reload", description="Recarrega uma ou todas as funcionalidades (Cogs).")
    @commands.is_owner()
    async def reload(self, ctx, cog: discord.Option(str, required=False)):
        if not cog:
            reloaded_cogs, error_cogs = [], []
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    cog_name = f'cogs.{filename[:-3]}'
                    try:
                        self.bot.unload_extension(cog_name)
                        self.bot.load_extension(cog_name)
                        reloaded_cogs.append(filename)
                    except Exception as e:
                        error_cogs.append(f"{filename}: {e}")
            if not error_cogs:
                await ctx.respond(f"✅ Todos os Cogs (`{', '.join(reloaded_cogs)}`) foram recarregados!", ephemeral=False)
            else:
                await ctx.respond(f"✅ Recarregados: `{', '.join(reloaded_cogs)}`\n❌ Erros: `{', '.join(error_cogs)}`", ephemeral=False)
        else:
            cog_name = f'cogs.{cog.lower()}'
            try:
                self.bot.unload_extension(cog_name)
                self.bot.load_extension(cog_name)
                await ctx.respond(f"✅ O Cog `{cog}.py` foi recarregado!", ephemeral=False)
            except Exception as e:
                await ctx.respond(f"❌ Erro ao recarregar o Cog `{cog}.py`: {e}", ephemeral=True)

    @advertir.error
    @banir.error
    @veravisos.error
    @removeradv.error
    @logs_advertencias.error
    @logs_bans.error
    async def permission_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("❌ Você não tem permissão para usar este comando!", ephemeral=True)
        else:
            self.log.error(f"Um erro ocorreu no comando '{ctx.command.name}': {error}", exc_info=True)
            await ctx.respond("Ocorreu um erro interno ao processar este comando.", ephemeral=True)

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.respond("❌ Apenas o dono do bot pode usar este comando!", ephemeral=True)
        else:
            self.log.error(f"Um erro ocorreu no comando 'reload': {error}", exc_info=True)
            await ctx.respond("Ocorreu um erro interno ao processar este comando.", ephemeral=True)

def setup(bot):
    bot.add_cog(Admin(bot))