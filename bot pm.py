import discord
from discord.ext import commands
import os
import asyncio
import config
# CORREÇÃO AQUI: Importa o painel direto do arquivo de dentro da pasta
from cogs_batalhao.cogs_batalhao import PainelPontoView

# --- CONFIGURAÇÃO DE INTENTS ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=config.PREFIXO, intents=intents)

# --- EVENTO QUANDO O BOT LIGA ---
@bot.event
async def on_ready():
    print(f"=========================================")
    print(f"🤖 BOT ONLINE: {bot.user.name}")
    print(f"🆔 ID DO BOT: {bot.user.id}")
    print(f"🚀 Pronto para garantir a segurança de Alemanha City!")
    print(f"=========================================")
    
    # Faz os botões do painel de ponto voltarem a funcionar se o bot reiniciar
    bot.add_view(PainelPontoView())

# --- LOGS DE AUDITORIA: MENSAGEM APAGADA ---
@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return

    canal_logs = message.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if not canal_logs:
        return

    embed = discord.Embed(
        title="🗑️ Relatório: Mensagem Apagada",
        description=f"Um membro apagou o conteúdo de uma transmissão.",
        color=config.COR_CRITICO,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="👤 Autor da Transmissão", value=message.author.mention, inline=True)
    embed.add_field(name="📍 Canal / Frequência", value=message.channel.mention, inline=True)
    
    conteudo = message.content if message.content else "*[Mensagem sem texto ou apenas mídia]*"
    embed.add_field(name="💬 Conteúdo Deletado", value=f"```\n{conteudo}\n```", inline=False)
    embed.set_footer(text=f"ID do Usuário: {message.author.id}")
    
    await canal_logs.send(embed=embed)

# --- LOGS DE AUDITORIA: MENSAGEM EDITADA ---
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content or not before.guild:
        return

    canal_logs = before.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if not canal_logs:
        return

    embed = discord.Embed(
        title="📝 Relatório: Mensagem Editada",
        description=f"Uma transmissão foi alterada na frequência.",
        color=config.COR_AVISO,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="👤 Autor da Transmissão", value=before.author.mention, inline=True)
    embed.add_field(name="📍 Canal / Frequência", value=before.channel.mention, inline=True)
    embed.add_field(name="❌ Conteúdo Antigo", value=f"```\n{before.content}\n```", inline=False)
    embed.add_field(name="✅ Conteúdo Novo", value=f"```\n{after.content}\n```", inline=False)
    embed.set_footer(text=f"ID do Usuário: {before.author.id}")
    
    await canal_logs.send(embed=embed)

# --- CARREGAR AS COGS AUTOMATICAMENTE ---
async def load_extensions():
    # Carrega o arquivo cogs_batalhao.py de dentro da pasta cogs_batalhao
    try:
        await bot.load_extension("cogs_batalhao.cogs_batalhao")
        print("📁 Módulo cogs_batalhao carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar o módulo cogs_batalhao: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
