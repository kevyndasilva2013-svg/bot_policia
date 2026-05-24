import discord
from discord.ext import commands
import asyncio
import config

# --- BOTÕES E VIEW DO PAINEL DE PONTO ---
class PainelPontoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Mantém os botões funcionando mesmo se o bot reiniciar

    @discord.ui.button(label="Entrar em Serviço", style=discord.ButtonStyle.green, custom_id="entrar_servico")
    async def entrar_servico(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal_logs = interaction.guild.get_channel(config.ID_CANAL_LOGS_PONTO)
        if canal_logs:
            embed = discord.Embed(
                title="🟢 Entrada em Serviço",
                description=f"O oficial {interaction.user.mention} iniciou o patrulhamento.",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await canal_logs.send(embed=embed)
        await interaction.response.send_message("✅ Você entrou em serviço com sucesso!", ephemeral=True)

    @discord.ui.button(label="Sair de Serviço", style=discord.ButtonStyle.red, custom_id="sair_servico")
    async def sair_servico(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal_logs = interaction.guild.get_channel(config.ID_CANAL_LOGS_PONTO)
        if canal_logs:
            embed = discord.Embed(
                title="🔴 Saída de Serviço",
                description=f"O oficial {interaction.user.mention} encerrou o patrulhamento.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await canal_logs.send(embed=embed)
        await interaction.response.send_message("❌ Você saiu de serviço!", ephemeral=True)


# --- CLASSE PRINCIPAL DOS COMANDOS (COG) ---
class CogsBatalhao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="painelponto")
    @commands.has_permissions(administrator=True)
    async def criar_painel(self, ctx):
        embed = discord.Embed(
            title="🚨 CENTRAL DE CONTROLE - BATALHÃO",
            description="Clique nos botões abaixo para gerenciar seu status de patrulhamento.\n\n"
                        "🟢 **Entrar em Serviço:** Registra o início do seu turno.\n"
                        "🔴 **Sair de Serviço:** Registra o fim do seu turno.",
            color=config.COR_PM
        )
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.set_footer(text="Mantenha o status atualizado de acordo com suas ações no servidor.")
        await ctx.send(embed=embed, view=PainelPontoView())

    # --- COMANDO: AVISO EM MASSA NO PRIVADO ---
    @commands.command(name="avisopv")
    @commands.has_permissions(administrator=True) # Apenas administradores / alta patente podem usar
    async def aviso_privado_massa(self, ctx, *, mensagem_aviso: str = None):
        if not mensagem_aviso:
            return await ctx.send("❌ **Uso incorreto!** Digite: `?avisopv [sua mensagem aqui]`")

        await ctx.send("📢 **Iniciando o envio de avisos no privado...** Isso pode demorar um pouco dependendo do tamanho do servidor.")

        sucesso = 0
        falha = 0

        # Cria a interface visual do aviso enviado na DM
        embed_pv = discord.Embed(
            title="🚨 NOTIFICAÇÃO OFICIAL - BATALHÃO",
            description="Olá, combatente.\n\nUma nova diretriz ou comunicado importante foi postado pela Alta Patente.",
            color=config.COR_PM
        )
        embed_pv.add_field(name="💬 Mensagem:", value=f"```text\n{mensagem_aviso}\n```", inline=False)
        embed_pv.add_field(name="📍 Onde visualizar:", value="Fique atento ao canal de **#avisos** ou **#comunicados** no nosso servidor principal.", inline=False)
        embed_pv.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed_pv.set_footer(text="Central de Notificações Automáticas")

        # Varre todos os membros do servidor de forma segura
        for membro in ctx.guild.members:
            if membro.bot:
                continue # Ignora outros robôs

            try:
                await membro.send(embed=embed_pv)
                sucesso += 1
                await asyncio.sleep(0.5) # Evita que o bot seja punido pelo Discord por spam (Rate Limit)
            except discord.Forbidden:
                falha += 1 # Ocorre se o membro tiver o privado bloqueado nas opções do Discord
            except Exception:
                falha += 1

        await ctx.send(f"✅ **Envio concluído!**\n📥 Receberam no PV: `{sucesso}` membros.\n❌ Privado fechado/bloqueado: `{falha}` membros.")


# --- FUNÇÃO DE REGISTRO DA COG ---
async def setup(bot):
    await bot.add_cog(CogsBatalhao(bot))
