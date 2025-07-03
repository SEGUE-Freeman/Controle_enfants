from flask import Flask, request, send_from_directory
from datetime import date, timedelta

app = Flask(__name__)

# 🔧 Génère le nom du fichier de présence du jour
def fichier_du_jour():
    return f"presence_{date.today().isoformat()}.txt"

# 🔧 Route principale — Formulaire HTML
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 🔧 Route pour enregistrer une présence
@app.route('/presence', methods=['POST'])
def enregistrer_presence():
    nom = request.form['nom'].strip()
    if nom:
        with open(fichier_du_jour(), 'a', encoding='utf-8') as f:
            f.write(nom + '\n')
    return f"""
        <h2>✅ Présence enregistrée pour {nom} aujourd'hui.</h2>
        <a href="/">➕ Enregistrer un autre campeur</a> | <a href="/comparer">📊 Voir le rapport</a>
    """

# 🔧 Route pour comparer aujourd’hui et hier
@app.route('/comparer')
def comparer():
    today = date.today()
    yesterday = today - timedelta(days=1)

    fichier_ajd = f"presence_{today.isoformat()}.txt"
    fichier_hier = f"presence_{yesterday.isoformat()}.txt"

    def lire(fichier):
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                return set(ligne.strip() for ligne in f if ligne.strip())
        except FileNotFoundError:
            return set()

    liste_ajd = lire(fichier_ajd)
    liste_hier = lire(fichier_hier)

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
