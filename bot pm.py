import discord
from discord.ext import commands
import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import config
from cogs_batalhao.cogs_batalhao import PainelPontoView, CogsBatalhao

# --- SERVIDOR WEB PARA A RENDER & UPTIME (CORRIGIDO) ---
class MutedWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot Online")
        
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
    def log_message(self, format, *args): return

def run_web_server():
    porta = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", porta), MutedWebServer)
    server.serve_forever()

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
    print(f"🚀 Comandos e Painel Prontos para Uso!")
    print(f"=========================================")
    bot.add_view(PainelPontoView())

# --- GUIA DE COMANDOS CRUSH-FIX ---
@bot.command(name="guia")
async def guia_comandos(ctx):
    embed = discord.Embed(
        title="📖 MANUAL DE COMANDOS - CENTRAL PM",
        description="Funções táticas disponíveis no bot:",
        color=config.COR_PM
    )
    embed.add_field(name="🚨 Painel de Ponto", value="`?painelponto` - Cria os botões de ponto.", inline=False)
    embed.add_field(name="📢 Comunicados", value="`?aviso [mensagem]` - Alerta geral para a tropa.", inline=False)
    embed.add_field(name="⭐ Promoções", value="`?up @membro [patente]` - Sobe patente de oficial.", inline=False)
    embed.add_field(name="⚠️ Corregedoria", value="`?adv @membro [motivo]` - Aplica advertência.", inline=False)
    embed.set_thumbnail(url=config.LOGO_POLICIA_URL)
    await ctx.send(embed=embed)

# --- LOGS DE AUDITORIA ---
@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild: return
    canal_logs = message.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if canal_logs:
        embed = discord.Embed(title="🗑️ Relatório: Mensagem Apagada", color=config.COR_CRITICO, timestamp=discord.utils.utcnow())
        embed.add_field(name="👤 Autor", value=message.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
        conteudo = message.content if message.content else "*[Mídia ou Vazio]*"
        embed.add_field(name="💬 Conteúdo", value=f"```\n{conteudo}\n```", inline=False)
        await canal_logs.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content or not before.guild: return
    canal_logs = before.guild.get_channel(config.ID_CANAL_LOGS_AUDITORIA)
    if canal_logs:
        embed = discord.Embed(title="📝 Relatório: Mensagem Editada", color=config.COR_AVISO, timestamp=discord.utils.utcnow())
        embed.add_field(name="👤 Autor", value=before.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="❌ Antigo", value=f"```\n{before.content}\n```", inline=False)
        embed.add_field(name="✅ Novo", value=f"```\n{after.content}\n```", inline=False)
        await canal_logs.send(embed=embed)

async def main():
    async with bot:
        # Força o registro manual da Cog sem depender do sistema de load_extension do discord
        await bot.add_cog(CogsBatalhao(bot))
        print("📁 Comandos do Batalhão sincronizados com sucesso!")
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
