from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import API_USER, API_KEY
from models import db, Claim, User
from datetime import datetime
import requests
import os

template_dir = os.path.abspath('../frontend/templates')
static_dir = os.path.abspath('../frontend/static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

app.config['SECRET_KEY'] = '9Y\Parrw+5*mgy~ES&a=Ew#I'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ra_dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    except: pass
    return None

def get_ra_game_info(game_id):
    url = "https://retroachievements.org/API/API_GetGame.php"
    params = {'z': API_USER, 'y': API_KEY, 'i': game_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200: return response.json()
    except: pass
    return None

# --- ROTAS PÚBLICAS ---

@app.route('/')
def index():
    all_claims = Claim.query.order_by(Claim.updated_at.desc()).all()
    active = [c for c in all_claims if c.status not in ['published', 'wishlist', 'jr_plan_wait', 'jr_queue']]
    return render_template('public.html', active=active, claims=all_claims)

@app.route('/future')
def future():
    all_claims = Claim.query.order_by(Claim.title).all()
    future_projects = [c for c in all_claims if c.status in ['wishlist', 'jr_plan_review', 'jr_plan_wait']]
    return render_template('public_future.html', future=future_projects, claims=all_claims)

@app.route('/published')
def published():
    all_claims = Claim.query.order_by(Claim.updated_at.desc()).all() 
    finished = [c for c in all_claims if c.status == 'published']
    return render_template('public_published.html', finished=finished, claims=all_claims)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        
        flash('Login inválido. Verifique usuário e senha.')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    claims = Claim.query.order_by(Claim.updated_at.desc()).all()
    current_time = datetime.utcnow()  # Adicione esta linha
    return render_template('index.html', claims=claims, current_time=current_time)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_claim():
    if request.method == 'POST':
        ra_id = request.form.get('ra_id')
        title = request.form.get('title')
        console = request.form.get('console')
        status = request.form.get('status')
        image_icon, console_icon = None, None

        if ra_id:
            data = get_ra_game_info(ra_id)
            if data and 'Title' in data:
                raw_img = data.get('ImageIcon', '')
                if raw_img: image_icon = raw_img.split('/')[-1].replace('.png', '')
                if not title: title = data.get('Title')
                if not console:
                    console = data.get('ConsoleName')
                    cid = data.get('ConsoleID')
                    if cid: console_icon = get_console_icon_url(cid)

        if title and console:
            new_claim = Claim(title=title, console=console, console_icon=console_icon,
                              ra_id=ra_id, image_icon=image_icon, status=status)
            db.session.add(new_claim)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
            
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_claim(id):
    claim = Claim.query.get_or_404(id)
    if request.method == 'POST':
        if 'delete' in request.form:
            db.session.delete(claim)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))

        claim.title = request.form.get('title')
        claim.status = request.form.get('status')
        claim.progress = request.form.get('progress')
        claim.notes = request.form.get('notes')
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit.html', claim=claim)

if __name__ == "__main__":
    app.run(debug=True)