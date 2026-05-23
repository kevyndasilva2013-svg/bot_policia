import discord
from discord.ext import commands
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

# --- SERVIDOR WEB PARA O UPTIMEROBOT (EVITA ERRO 501 HEAD) ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🚓 Corregedoria Policial Online 24/7!".encode('utf-8'))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def log_message(self, format, *args):
        return

def iniciar_servidor_web():
    porta = int(os.environ.get("PORT", 8080))
    server_address = ('0.0.0.0', porta)
    httpd = HTTPServer(server_address, WebServerHandler)
    print(f"🌐 Servidor Web ativo na porta {porta}.")
    httpd.serve_forever()

threading.Thread(target=iniciar_servidor_web, daemon=True).start()

# --- CONFIGURAÇÃO DO BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

bot = commands.Bot(command_prefix="?", intents=intents)

# 💾 SEU CANAL CORRETO ATUALIZADO
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
    if before.author.bot or before.content == after.content or not before.guild:
        return

    canal_logs = before.guild.get_channel(ID_CANAL_LOGS_AUDITORIA)
    if canal_logs:
        embed = discord.Embed(
            title="✏️ Relatório: Mensagem Editada",
            description="Uma transmissão foi alterada após o envio.",
            color=COR_AVISO,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=f"{before.author.name} (ID: {before.author.id})", icon_url=before.author.display_avatar.url)
        embed.set_thumbnail(url=LOGO_POLICIA_URL)
        
        embed.add_field(name="👤 Autor", value=before.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="🔗 Link da Mensagem", value=f"[Ir para Mensagem]({after.jump_url})", inline=True)

        embed.add_field(name="🛑 Conteúdo Original", value=f"```text\n{before.content}\n```", inline=False)
        embed.add_field(name="✅ Novo Conteúdo", value=f"```text\n{after.content}\n```", inline=False)
        
        await canal_logs.send(embed=embed)

# --- 3. LOGS DE MEMBRO: SAIU DO SERVIDOR ---
@bot.event
async def on_member_remove(member):
    canal_logs = member.guild.get_channel(ID_CANAL_LOGS_AUDITORIA)
    if canal_logs:
        embed = discord.Embed(
            title="🏃 Membro Saiu do QAP",
            description="Um membro deslogou do servidor do Discord.",
            color=COR_AVISO,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=LOGO_POLICIA_URL)
        
        embed.add_field(name="👤 Usuário", value=f"{member.mention}\n`{member.name}`", inline=True)
        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
        
        cargos = [role.mention for role in member.roles if role != member.guild.default_role]
        lista_cargos = ", ".join(cargos) if cargos else "Nenhum cargo ativo"
        embed.add_field(name="🎖️ Patentes e Especializações", value=lista_cargos, inline=False)
        
        await canal_logs.send(embed=embed)

# --- 4. LOGS DE MEMBRO: ENTROU NO SERVIDOR ---
@bot.event
async def on_member_join(member):
    canal_logs = member.guild.get_channel(ID_CANAL_LOGS_AUDITORIA)
    if canal_logs:
        embed = discord.Embed(
            title="📥 Novo Membro Apresentado",
            description="Um novo usuário se apresentou no servidor.",
            color=COR_SUCESSO,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=LOGO_POLICIA_URL)
        
        embed.add_field(name="👤 Usuário", value=f"{member.mention}\n`{member.name}`", inline=True)
        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
        
        criacao_conta = member.created_at.strftime("%d/%m/%Y às %H:%M")
        idade_conta = datetime.utcnow() - member.created_at.replace(tzinfo=None)
        
        embed.add_field(name="📅 Conta Criada em", value=criacao_conta, inline=True)
        embed.add_field(name="⏳ Idade da Conta", value=f"{idade_conta.days} dias", inline=True)
        
        await canal_logs.send(embed=embed)

# 🔐 PUXA O TOKEN DE FORMA INVISÍVEL E SEGURO DIRETO DA RENDER
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)