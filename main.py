import os
import sqlite3
import threading
import discord
from discord.ext import commands
from flask import Flask, render_template

# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "clan_data.db"))

# --- CONFIGURACIÓN DEL BOT ---
# IMPORTANTE: Sacamos el token de las variables de entorno de Koyeb
TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- JERARQUÍA POR ID (Moon Galactic Regimen) ---
JERARQUIA_ROLES = {
    1430770043951644692: {"nombre": "TIER MUNDIAL", "puntos": 3000},
    1430770044329263134: {"nombre": "TIER NACIONAL", "puntos": 2000},
    1430770053061804155: {"nombre": "TIER S+", "puntos": 1650},
    1430770049999704154: {"nombre": "TIER S", "puntos": 1500},
    1430770041879527435: {"nombre": "TIER A+", "puntos": 1350},
    1448084469948092436: {"nombre": "TIER A", "puntos": 1250},
    1430770054101995572: {"nombre": "TIER B+", "puntos": 1150},
    1430770054093606955: {"nombre": "TIER B", "puntos": 1050},
    1430770051174371389: {"nombre": "TIER C+", "puntos": 900},
    1430770053376114698: {"nombre": "TIER C", "puntos": 850},
    1430767573481291786: {"nombre": "TIER D+", "puntos": 700},
    1430759282680397846: {"nombre": "TIER D", "puntos": 600},
    1430770042521518131: {"nombre": "TIER E+", "puntos": 550},
    1430770052361355337: {"nombre": "TIER E", "puntos": 500}
}

def asegurar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS members 
                      (username TEXT PRIMARY KEY, elo INTEGER, rango TEXT, avatar TEXT)''')
    conn.commit()
    conn.close()

# --- RUTA WEB (Flask para la página de Ranking) ---
@app.route('/')
def ranking():
    try:
        asegurar_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT username, elo, rango, avatar FROM members ORDER BY elo DESC")
        jugadores = cursor.fetchall()
        conn.close()
        return render_template('ranking.html', jugadores=jugadores, activos=len(jugadores))
    except Exception as e:
        return f"Error en la web: {e}"

# --- EVENTOS Y COMANDOS DEL BOT ---
@bot.event
async def on_ready():
    asegurar_db()
    print(f"✅ Bot MGR Conectado: {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def sincronizar(ctx):
    asegurar_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members") 
    contador = 0
    for m in ctx.guild.members:
        if m.bot: continue
        datos_rango = None
        for role_id, info in JERARQUIA_ROLES.items():
            if m.get_role(role_id):
                datos_rango = info
                break 
        if datos_rango:
            cursor.execute("INSERT OR REPLACE INTO members VALUES (?, ?, ?, ?)", 
                           (m.display_name, datos_rango["puntos"], datos_rango["nombre"], str(m.display_avatar.url)))
            contador += 1
    conn.commit()
    conn.close()
    await ctx.send(f"🔄 **Sincronización completa.** {contador} miembros añadidos.")

@bot.command()
@commands.has_permissions(administrator=True)
async def add_elo(ctx, usuario: discord.Member, cantidad: int):
    asegurar_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT elo FROM members WHERE username = ?", (usuario.display_name,))
    fila = cursor.fetchone()
    if fila:
        nuevo = fila[0] + cantidad
        cursor.execute("UPDATE members SET elo = ? WHERE username = ?", (nuevo, usuario.display_name))
        conn.commit()
        await ctx.send(f"📈 +{cantidad} pts para **{usuario.display_name}**. Total: {nuevo}")
    conn.close()

@bot.command()
@commands.has_permissions(administrator=True)
async def rem_elo(ctx, usuario: discord.Member, cantidad: int):
    asegurar_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT elo FROM members WHERE username = ?", (usuario.display_name,))
    fila = cursor.fetchone()
    if fila:
        nuevo = max(0, fila[0] - cantidad)
        cursor.execute("UPDATE members SET elo = ? WHERE username = ?", (nuevo, usuario.display_name))
        conn.commit()
        await ctx.send(f"📉 -{cantidad} pts para **{usuario.display_name}**. Total: {nuevo}")
    conn.close()

# --- LANZAMIENTO DUAL ---
def run_discord():
    if not TOKEN:
        print("❌ ERROR: Falta DISCORD_TOKEN en las variables de entorno.")
        return
    bot.run(TOKEN)

if __name__ == "__main__":
    threading.Thread(target=run_discord).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
