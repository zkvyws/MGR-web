from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

# Ruta de la base de datos (misma que el bot)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "clan_data.db"))

@app.route('/')
def ranking():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # IMPORTANTE: Seleccionamos las 4 columnas incluyendo 'avatar'
        cursor.execute("SELECT username, elo, rango, avatar FROM members ORDER BY elo DESC")
        jugadores = cursor.fetchall()
        conn.close()
        
        # Estadísticas básicas
        activos = len(jugadores)
        
        return render_template('ranking.html', jugadores=jugadores, activos=activos)
    except Exception as e:
        return f"Error en la base de datos: {e}. Asegúrate de ejecutar el bot primero."

if __name__ == '__main__':
    app.run(debug=True)
