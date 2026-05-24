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
        embed.set_thumbnail(url
