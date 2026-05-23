import discord
from discord.ext import commands
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

# --- SERVIDOR WEB INTELIGENTE PARA EVITAR ERRO 502 E 501 ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🚓 Corregedoria Policial Online!".encode('utf-8'))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def log_message(self, format, *args):
        return  # Desativa logs pesados no terminal para rodar mais rápido

def iniciar_servidor_web():
    # A Render exige ler a porta da variável de ambiente, se não achar usa a 10000 padrão deles
    porta = int(os.environ.get("PORT", 10000))
    server_address = ('0.0.0.0', porta)
    httpd = HTTPServer(server_address, WebServerHandler)
    print(f"🌐 Servidor de Redirecionamento ativo na porta {porta}.")
    httpd.serve_forever()

# Iniciamos o servidor web antes de qualquer coisa para a Render validar o IP na hora
threading.Thread(target=iniciar_servidor_web, daemon=True).start()

# --- CONFIGURAÇÃO DO BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

bot = commands.Bot(command_prefix="?", intents=intents)

# 💾 CONFIGURAÇÕES FIXAS
ID_CANAL_LOGS_AUDITORIA = 1507611818347200613
LOGO_POLICIA_URL = "https://raw.githubusercontent.com/KevynDaSilva/bot_fvm_logs/main/assets/image_13.png" 

COR_ERRO_CRITICO = 0xFF0000     # Vermelho (Apagado)
COR_AVISO = 0xFFAA00            # Laranja (Editado, Saiu)
COR_SUCESSO = 0x00FF00          # Verde (Entrou)

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"🚨 CORREGEDORIA POLICIAL ATIVA!")
    print(f"🤖 Bot de Auditoria: {bot.user.name}")
    print("=" * 50)

# --- 1. LOGS DE MENSAGEM: APAGADA ---
@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return

    canal_logs = message.guild.get_channel(ID_CANAL_LOGS_AUDITORIA)
    if canal_logs:
        embed = discord.Embed(
            title="🗑️ Relatório: Mensagem Apagada",
            description="Um membro apagou o conteúdo de uma transmissão.",
            color=COR_ERRO_CRITICO,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=f"{message.author.name} (ID: {message.author.id})", icon_url=message.author.display_avatar.url)
        embed.set_thumbnail(url=LOGO_POLICIA_URL)
        
        embed.add_field(name="👤 Autor da Transmissão", value=message.author.mention, inline=True)
        embed.add_field(name="📍 Canal / Frequência", value=message.channel.mention, inline=True)
        
        conteudo = message.content if message.content else "*[Mídia ou Conteúdo Vazios]*"
        embed.add_field(name="💬 Conteúdo Deletado", value=f"```text\n{conteudo}\n```", inline=False)
        
        await canal_logs.send(embed=embed)

# --- 2. LOGS DE MENSAGEM: EDITADA ---
@bot.event
async def on_message_edit(before, after):
    if before.author.
