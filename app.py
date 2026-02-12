from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli-anahtar-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Klasör yoksa oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Gelişmiş Kullanıcı Modeli ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    # --- Dosyalar (URL veya Dosya Yolu) ---
    background_url = db.Column(db.String(500), default="")
    profile_pic_url = db.Column(db.String(500), default="https://cdn.discordapp.com/embed/avatars/0.png")
    audio_url = db.Column(db.String(500), default="")
    cursor_url = db.Column(db.String(500), default="")
    
    # --- Genel Özelleştirme ---
    display_name = db.Column(db.String(50), default="Kullanıcı")
    description = db.Column(db.String(300), default="")
    location = db.Column(db.String(50), default="")
    discord_rpc = db.Column(db.Boolean, default=False) # Discord Presence
    
    # --- Görünüm Ayarları ---
    profile_opacity = db.Column(db.Integer, default=50) # 0-100
    profile_blur = db.Column(db.Integer, default=10)    # 0-100 px
    
    # --- Renk Özelleştirme ---
    accent_color = db.Column(db.String(20), default="#ffffff")
    text_color = db.Column(db.String(20), default="#ffffff")
    bg_color = db.Column(db.String(20), default="#080808")
    icon_color = db.Column(db.String(20), default="#ffffff")
    
    # --- Diğer Özellikler ---
    monochrome_icons = db.Column(db.Boolean, default=False)
    animated_title = db.Column(db.Boolean, default=False)
    badge_glow = db.Column(db.Boolean, default=False)
    
    # --- Sosyal Medya (JSON yerine basit sütunlar) ---
    discord = db.Column(db.String(200), default="")
    instagram = db.Column(db.String(200), default="")
    youtube = db.Column(db.String(200), default="")
    spotify = db.Column(db.String(200), default="")
    tiktok = db.Column(db.String(200), default="")
    twitter = db.Column(db.String(200), default="")
    telegram = db.Column(db.String(200), default="")
    custom_link = db.Column(db.String(200), default="")
    
    view_count = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helper: Dosya Yükleme ---
def save_file(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return url_for('static', filename='uploads/' + filename)
    return None

# --- Rotalar ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Hatalı giriş.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Kullanıcı adı dolu.', 'error')
            return redirect(url_for('register'))
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Dosya Yüklemeleri (Varsa yükle, yoksa formdaki URL'yi al)
        bg_file = request.files.get('bg_file')
        if bg_file: current_user.background_url = save_file(bg_file)
        elif request.form.get('background_url'): current_user.background_url = request.form.get('background_url')

        av_file = request.files.get('avatar_file')
        if av_file: current_user.profile_pic_url = save_file(av_file)
        elif request.form.get('profile_pic_url'): current_user.profile_pic_url = request.form.get('profile_pic_url')
        
        au_file = request.files.get('audio_file')
        if au_file: current_user.audio_url = save_file(au_file)
        elif request.form.get('audio_url'): current_user.audio_url = request.form.get('audio_url')

        # Text Alanları
        current_user.description = request.form.get('description')
        current_user.location = request.form.get('location')
        
        # Renkler & Sliderlar
        current_user.profile_opacity = request.form.get('profile_opacity')
        current_user.profile_blur = request.form.get('profile_blur')
        current_user.accent_color = request.form.get('accent_color')
        current_user.text_color = request.form.get('text_color')
        current_user.bg_color = request.form.get('bg_color')
        current_user.icon_color = request.form.get('icon_color')
        
        # Toggle Switchler (Checkbox gelmezse False yap)
        current_user.monochrome_icons = 'monochrome_icons' in request.form
        current_user.animated_title = 'animated_title' in request.form
        current_user.badge_glow = 'badge_glow' in request.form
        current_user.discord_rpc = 'discord_rpc' in request.form
        
        # Sosyal Medya
        current_user.discord = request.form.get('discord')
        current_user.instagram = request.form.get('instagram')
        current_user.youtube = request.form.get('youtube')
        current_user.spotify = request.form.get('spotify')
        current_user.telegram = request.form.get('telegram')
        
        db.session.commit()
        flash('Profil güncellendi!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('dashboard.html', user=current_user)

@app.route('/<username>')
def profile(username):
    user = User.query.filter_by(username=username.lower()).first()
    if not user: return "Kullanıcı bulunamadı", 404
    user.view_count += 1
    db.session.commit()
    return render_template('profile.html', user=user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)