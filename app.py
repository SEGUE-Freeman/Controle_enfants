from flask import Flask, request, send_from_directory
from datetime import date, timedelta
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'presences.db'

# 🔧 Initialise la base si elle n'existe pas encore
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS presences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# 🔧 Route principale — Formulaire HTML
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 🔧 Enregistrement de présence dans la base
@app.route('/presence', methods=['POST'])
def enregistrer_presence():
    nom = request.form['nom'].strip()
    if nom:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO presences (nom, date) VALUES (?, ?)', (nom, date.today().isoformat()))
            conn.commit()
    return f"""
        <h2>✅ Présence enregistrée pour {nom} aujourd'hui.</h2>
        <a href="/">➕ Enregistrer un autre campeur</a> | 
        <a href="/comparer">📊 Voir le rapport</a>
    """

# 🔧 Comparaison des présences entre aujourd’hui et hier
@app.route('/comparer')
def comparer():
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT nom FROM presences WHERE date = ?', (today,))
        liste_ajd = set(row[0] for row in c.fetchall())

        c.execute('SELECT nom FROM presences WHERE date = ?', (yesterday,))
        liste_hier = set(row[0] for row in c.fetchall())

    absents = liste_hier - liste_ajd
    nouveaux = liste_ajd - liste_hier

    return f"""
        <h2>📋 Résultat du contrôle de présence</h2>

        <h3>🆕 Nouveaux aujourd’hui ({len(nouveaux)}) :</h3>
        <ul>{''.join(f'<li>{nom}</li>' for nom in sorted(nouveaux)) or '<li>Aucun</li>'}</ul>

        <h3>❌ Absents aujourd’hui ({len(absents)}) :</h3>
        <ul>{''.join(f'<li>{nom}</li>' for nom in sorted(absents)) or '<li>Aucun</li>'}</ul>

        <a href="/">➕ Enregistrer un autre campeur</a>
    """

if __name__ == '__main__':
    app.run(debug=True)


from flask import send_file
import csv

# 🔧 Route pour télécharger la liste de présence du jour au format CSV
@app.route('/telecharger')
def telecharger():
    fichier = 'presences_du_jour.csv'
    date_du_jour = date.today().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT nom FROM presences WHERE date = ?', (date_du_jour,))
        lignes = c.fetchall()

    # 🔧 Écrit dans un fichier CSV
    with open(fichier, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nom', 'Date'])  # En-tête
        for ligne in lignes:
            writer.writerow([ligne[0], date_du_jour])

    return send_file(fichier, as_attachment=True)
