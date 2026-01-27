from flask import Flask, render_template, request, redirect, url_for, flash
from config import API_USER, API_KEY
from models import db, Claim
import requests
import os

template_dir = os.path.abspath('../frontend/templates')
static_dir = os.path.abspath('../frontend/static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ra_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

def get_ra_game_info(game_id):

    url = "https://retroachievements.org/API/API_GetGame.php"
    params = {
        'z': API_USER,
        'y': API_KEY,
        'i': game_id
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/')
def index():
    claims = Claim.query.order_by(Claim.updated_at.desc()).all()
    return render_template('index.html', claims=claims)

@app.route('/add', methods=['GET', 'POST'])
def add_claim():
    if request.method == 'POST':
        ra_id = request.form.get('ra_id')
        title = request.form.get('title')
        console = request.form.get('console')
        status = request.form.get('status')
        image_icon = None

        if ra_id:
            try:
                game_data = get_ra_game_info(ra_id)
                if game_data and 'Title' in game_data:
                    image_icon = game_data.get('ImageIcon')
                    if not title:
                        title = game_data.get('Title')
                    if not console:
                        console = game_data.get('ConsoleName')
            except Exception as e:
                print(f"Erro na API: {e}")

            if title and console:
                new_claim = Claim(
                    title=title,
                    console=console,
                    ra_id=ra_id if ra_id else None,
                    image_icon=image_icon,
                    status=status
                )
                db.session.add(new_claim)
                db.session.commit()
                return redirect(url_for('index'))
    return render_template('add.html')

if __name__ == "__main__":
    app.run(debug=True)