import discord
from discord.ext import commands
import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import config
from cogs_batalhao.cogs_batalhao import PainelPontoView

# --- SISTEMA PARA ENGANAR A RENDER (PORT BINDING) ---
class MutedWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot Online")
    def log_message(self, format, *args):
        return

def run_web_server():
    porta = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", porta), MutedWebServer)
    server.serve_forever()

# Liga o servidor web em segundo plano antes do bot
threading.Thread(target=run_web_server, daemon=True).start()

# --- CONFIGURAÇÃO DE INTENTS ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=config.PREFIXO, intents=intents)

@bot.event
async def on_ready():
    print(f"=========================================")
    print(f"🤖 BOT ONLINE: {bot.user.name}")
    print(f"🚀 Sistema de Portas e Cogs Alinhados!")
    print(f"=========================================")
    bot.add_view(PainelPontoView())

# --- GUIA DE COMANDOS COMPLETO ---
@bot.command(name="guia")
async def guia_comandos(ctx):
    embed = discord.Embed(
        title="📖 MANUAL DE COMANDOS - CENTRAL PM",
        description="Aqui estão as funções administrativas disponíveis para a alta patente:",
        color=config.COR_PM
    )
    embed.add_field(name="🚨 Painel de Ponto", value="`?painelponto` - Gera o painel com os botões de entrada/saída.", inline=False)
    embed.add_field(name="📢 Comunicados", value="`?aviso [mensagem]` - Envia um anúncio geral marcando @everyone.", inline=False)
    embed.add_field(name="⭐ Promoções", value="`?up @membro [nova patente]` - Registra a ascensão de um oficial.", inline=False)
    embed.add_field(name="⚠️ Corregedoria", value="`?adv @membro [motivo]` - Aplica uma advertência formal.", inline=False)
    embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
    embed.set_footer(text="Apenas para oficiais autorizados.")
    await ctx.send(embed=embed)

# --- LOGS DE AUDITORIA: MENSAGEM APAGADA ---
@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild: return
    canal_logs = message.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if not canal_logs: return

    embed = discord.Embed(title="🗑️ Relatório: Mensagem Apagada", color=config.COR_CRITICO, timestamp=discord.utils.utcnow())
    embed.add_field(name="👤 Autor", value=message.author.mention, inline=True)
    embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
    conteudo = message.content if message.content else "*[Mensagem vazia ou mídia]*"
    embed.add_field(name="💬 Conteúdo", value=f"```\n{conteudo}\n```", inline=False)
    await canal_logs.send(embed=embed)

# --- LOGS DE AUDITORIA: MENSAGEM EDITADA ---
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content or not before.guild: return
    canal_logs = before.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if not canal_logs: return

    embed = discord.Embed(title="📝 Relatório: Mensagem Editada", color=config.COR_AVISO, timestamp=discord.utils.utcnow())
    embed.add_field(name="👤 Autor", value=before.author.mention, inline=True)
    embed.add_field(name="📍 Canal", value=before.channel.mention, inline=True)
    embed.add_field(name="❌ Antigo", value=f"```\n{before.content}\n```", inline=False)
    embed.add_field(name="✅ Novo", value=f"```\n{after.content}\n```", inline=False)
    await canal_logs.send(embed=embed)

async def load_extensions():
    try:
        await bot.load_extension("cogs_batalhao.cogs_batalhao")
        print("📁 Módulo cogs_batalhao carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar o módulo: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
