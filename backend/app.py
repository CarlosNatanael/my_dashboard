from flask import Flask, render_template
from config import API_USER, API_KEY
from models import db, Claim
import requests

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)