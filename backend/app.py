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

def get_console_icon_url(target_console_id):
    url = "https://retroachievements.org/API/API_GetConsoleIDs.php"
    params = {'z': API_USER, 'y': API_KEY}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            consoles = response.json()
            for console in consoles:
                if console.get('ID') == int(target_console_id):
                    return console.get('IconURL')
    except Exception as e:
        print(f"Erro ao buscar icone do console: {e}")
    return None

def get_ra_game_info(game_id):
    url = "https://retroachievements.org/API/API_GetGame.php"
    params = {'z': API_USER, 'y': API_KEY, 'i': game_id}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro ao buscar info do jogo: {e}")
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
        console_icon = None

        if ra_id:
            try:
                game_data = get_ra_game_info(ra_id)
                if game_data and 'Title' in game_data:
                    raw_image = game_data.get('ImageIcon', '')
                    if raw_image:
                        image_icon = raw_image.split('/')[-1].replace('.png', '')
                    
                    if not title:
                        title = game_data.get('Title')
                    if not console:
                        console = game_data.get('ConsoleName')
                        console_id = game_data.get('ConsoleID')

                        if console_id:
                            console_icon = get_console_icon_url(console_id)
                            
            except Exception as e:
                print(f"Erro na API: {e}")

        if title and console:
            new_claim = Claim(
                title=title,
                console=console,
                console_icon=console_icon,
                ra_id=ra_id if ra_id else None,
                image_icon=image_icon,
                status=status
            )
            db.session.add(new_claim)
            db.session.commit()
            return redirect(url_for('index'))
            
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_claim(id):
    claim = Claim.query.get_or_404(id)

    if request.method == 'POST':
        if 'delete' in request.form:
            db.session.delete(claim)
            db.session.commit()
            return redirect(url_for('index'))

        claim.title = request.form.get('title')
        claim.status = request.form.get('status')
        claim.progress = request.form.get('progress')
        claim.notes = request.form.get('notes')
        
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', claim=claim)

@app.route('/portfolio')
def portfolio():
    all_claims = Claim.query.order_by(Claim.title).all()
    active_projects = [c for c in all_claims if c.status not in ['published', 'wishlist']]
    finished_projects = [c for c in all_claims if c.status == 'published']
    future_projects = [c for c in all_claims if c.status == 'wishlist']
    
    return render_template('public.html', 
                         active=active_projects, 
                         finished=finished_projects,
                         future=future_projects)

if __name__ == "__main__":
    app.run(debug=True)