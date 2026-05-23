import discord
from discord.ext import commands
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
import logging
import config
from cogs_batalhao import PainelPontoView

# --- SISTEMA DE LOGS INTERNO PROFISSIONAL ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("BatalhaoCentral")

# --- SERVIDOR WEB FAIL-SAFE (ANTI ERRO 502) ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🚓 Central de Monitoramento PM Ativa!".encode('utf-8'))
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        return # Silencia flood no console da Render

def iniciar_servidor():
    porta = int(os.environ.get("PORT", 10000))
    try:
        httpd = HTTPServer(('0.0.0.0', porta), WebServerHandler)
        logger.info(f"🌐 Servidor Web ativo com sucesso na porta {porta}.")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"❌ Erro Crítico no Servidor Web: {e}")

threading.Thread(target=iniciar_servidor, daemon=True).start()

# --- INSTÂNCIA DO BOT CENTRAL ---
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

bot = commands.Bot(command_prefix=config.PREFIXO, intents=intents)

@bot.event
async def on_ready():
    logger.info("=" * 40)
    logger.info(f"🚨 BOT CENTRAL LOGADO COMO: {bot.user.name}")
    logger.info("=" * 40)
    
    # Valida duplicidade antes de registrar view persistente
    if not any(isinstance(v, PainelPontoView) for v in bot.persistent_views):
        bot.add_view(PainelPontoView())
        logger.info("🎛️ Painel Interativo de Ponto registrado com sucesso!")

# --- EVENTOS DE AUDITORIA INTERNA (LOGS GERAIS) ---
@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild: return
    canal = message.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if canal:
        embed = discord.Embed(title="🗑️ Relatório: Mensagem Apagada", color=config.COR_CRITICO, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{message.author.name} (ID: {message.author.id})", icon_url=message.author.display_avatar.url)
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.add_field(name="👤 Autor", value=message.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
        conteudo = message.content if message.content else "*[Mídia ou Conteúdo Vazio]*"
        embed.add_field(name="💬 Conteúdo Deletado", value=f"```text\n{conteudo}\n```", inline=False)
        await canal.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content or not before.guild: return
    canal = before.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if canal:
        embed = discord.Embed(title="✏️ Relatório: Mensagem Editada", color=config.COR_AVISO, timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{before.author.name} (ID: {before.author.id})", icon_url=before.author.display_avatar.url)
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.add_field(name="👤 Autor", value=before.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="🛑 Original", value=f"```text\n{before.content}\n```", inline=False)
        embed.add_field(name="✅ Novo Conteúdo", value=f"```text\n{after.content}\n```", inline=False)
        await canal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    canal = member.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if canal:
        embed = discord.Embed(title="🏃 Membro Saiu do Discord", color=config.COR_AVISO, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.add_field(name="👤 Usuário", value=f"{member.mention}\n`{member.name}`", inline=True)
        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
        await canal.send(embed=embed)

@bot.event
async def on_member_join(member):
    canal = member.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if canal:
        embed = discord.Embed(title="📥 Novo Membro Entrou", color=config.COR_SUCESSO, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
        embed.add_field(name="👤 Usuário", value=f"{member.mention}\n`{member.name}`", inline=True)
        await canal.send(embed=embed)

# --- CARREGAMENTO ASSÍNCRONO DOS MÓDULOS ---
async def carregar_modulos():
    try:
        await bot.load_extension("cogs_batalhao")
        logger.info("📦 Módulo 'cogs_batalhao' acoplado com sucesso.")
    except Exception as e:
        logger.error(f"❌ Falha ao carregar extensões: {e}")

# DISPARO INICIAL DO BOT
async def main():
    async with bot:
        await carregar_modulos()
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
