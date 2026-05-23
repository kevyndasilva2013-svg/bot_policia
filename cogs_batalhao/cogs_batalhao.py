import discord
from discord.ext import commands
import config

# --- BOTÕES INTERATIVOS DO PAINEL DE PONTO ---
class PainelPontoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Mantém os botões funcionando mesmo se o bot reiniciar

    @discord.ui.button(label="Entrar em Serviço", style=discord.ButtonStyle.success, custom_id="entrar_servico", emoji="🪖")
    async def entrar_servico(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal_logs = interaction.guild.get_channel(config.ID_LOGS_BATER_PONTO)
        embed = discord.Embed(
            title="⚡ QAP | Entrada de Serviço",
            description=f"O oficial {interaction.user.mention} iniciou o patrulhamento.",
            color=config.COR_SUCESSO,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        
        if canal_logs:
            await canal_logs.send(embed=embed)
        await interaction.response.send_message("🟢 Você entrou em serviço com sucesso!", ephemeral=True)

    @discord.ui.button(label="Sair de Serviço", style=discord.ButtonStyle.danger, custom_id="sair_servico", emoji="📴")
    async def sair_servico(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal_logs = interaction.guild.get_channel(config.ID_LOGS_BATER_PONTO)
        embed = discord.Embed(
            title="💤 QRU | Saída de Serviço",
            description=f"O oficial {interaction.user.mention} encerrou o patrulhamento.",
            color=config.COR_CRITICO,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        
        if canal_logs:
            await canal_logs.send(embed=embed)
        await interaction.response.send_message("🔴 Você saiu de serviço!", ephemeral=True)

# --- COG DE COMANDOS DO BATALHÃO ---
class CogsBatalhao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando para criar o painel no chat de bater ponto
    @commands.command(name="painelponto")
    @commands.has_permissions(administrator=True)
    async def enviar_painel(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(
            title="🚔 CENTRAL POLÍCIA MILITAR - SISTEMA DE PONTO",
            description="Clique nos botões abaixo para gerenciar o seu status de patrulhamento no batalhão.\n\n"
                        "**🪖 ENTRAR EM SERVIÇO:** Registra seu início de QAP.\n"
                        "**📴 SAIR DE SERVIÇO:** Registra seu término de turno.",
            color=config.COR_PM
        )
        embed.set_image(url=config.LOGO_POLICIA_URL)
        embed.set_footer(text="Mantenha a cidade segura. Comando Geral da PM.")
        
        await ctx.send(embed=embed, view=PainelPontoView())

    # COMANDO DE AVISOS
    @commands.command(name="aviso")
    @commands.has_permissions(manage_messages=True)
    async def comando_aviso(self, ctx, *, mensagem: str):
        await ctx.message.delete()
        chat_publico = ctx.guild.get_channel(config.ID_CHAT_AVISOS)
        chat_logs = ctx.guild.get_channel(config.ID_LOGS_AVISOS)
        
        embed = discord.Embed(title="📢 COMUNICADO OFICIAL", description=mensagem, color=config.COR_AVISO, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.set_footer(text=f"Enviado por: {ctx.author.name}")
        
        if chat_publico: await chat_publico.send(content="@everyone", embed=embed)
        if chat_logs: await chat_logs.send(embed=embed)

    # COMANDO DE PROMOÇÕES / UPAMENTOS
    @commands.command(name="up")
    @commands.has_permissions(manage_roles=True)
    async def comando_up(self, ctx, membro: discord.Member, *, nova_patente: str):
        await ctx.message.delete()
        chat_publico = ctx.guild.get_channel(config.ID_CHAT_UPAMENTOS)
        chat_logs = ctx.guild.get_channel(config.ID_LOGS_UPAMENTOS)
        
        embed = discord.Embed(title="⭐ PROMOÇÃO DE PATENTE", description=f"O oficial {membro.mention} foi promovido para **{nova_patente}**! Parabéns pelo empenho.", color=config.COR_SUCESSO, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.set_footer(text=f"Promovido por: {ctx.author.name}")
        
        if chat_publico: await chat_publico.send(embed=embed)
        if chat_logs: await chat_logs.send(embed=embed)

    # COMANDO DE ADVERTÊNCIA
    @commands.command(name="adv")
    @commands.has_permissions(manage_roles=True)
    async def comando_adv(self, ctx, membro: discord.Member, *, motivo: str):
        await ctx.message.delete()
        chat_publico = ctx.guild.get_channel(config.ID_CHAT_ADVERTENCIA)
        chat_logs = ctx.guild.get_channel(config.ID_LOGS_ADVERTENCIA)
        
        embed = discord.Embed(title="⚠️ ADVERTÊNCIA APLICADA", description=f"O oficial {membro.mention} recebeu uma advertência formal.\n\n**Motivo:** {motivo}", color=config.COR_CRITICO, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.set_footer(text=f"Aplicado por: {ctx.author.name}")
        
        if chat_publico: await chat_publico.send(embed=embed)
        if chat_logs: await chat_logs.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CogsBatalhao(bot))
