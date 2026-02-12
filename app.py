from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cok-gizli-anahtar-3482-x'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Klasör yoksa oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- KULLANICI MODELİ ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    # Dosyalar
    background_url = db.Column(db.String(500), default="")
    profile_pic_url = db.Column(db.String(500), default="https://cdn.discordapp.com/embed/avatars/0.png")
    audio_url = db.Column(db.String(500), default="")
    
    # Özelleştirme
    display_name = db.Column(db.String(50), default="")
    description = db.Column(db.String(300), default="")
    location = db.Column(db.String(50), default="")
    discord_rpc = db.Column(db.Boolean, default=False)
    
    # Görünüm
    profile_opacity = db.Column(db.Integer, default=50)
    profile_blur = db.Column(db.Integer, default=10)
    
    # Renkler
    accent_color = db.Column(db.String(20), default="#ffffff")
    text_color = db.Column(db.String(20), default="#ffffff")
    bg_color = db.Column(db.String(20), default="#080808")
    icon_color = db.Column(db.String(20), default="#ffffff")
    
    # Switchler
    monochrome_icons = db.Column(db.Boolean, default=False)
    animated_title = db.Column(db.Boolean, default=False)
    badge_glow = db.Column(db.Boolean, default=False)
    
    # Sosyal Medya
    discord = db.Column(db.String(200), default="")
    instagram = db.Column(db.String(200), default="")
    youtube = db.Column(db.String(200), default="")
    spotify = db.Column(db.String(200), default="")
    tiktok = db.Column(db.String(200), default="")
    twitter = db.Column(db.String(200), default="")
    telegram = db.Column(db.String(200), default="")
    
    view_count = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- TABLOLARI OLUŞTUR (Render İçin Kritik) ---
with app.app_context():
    db.create_all()

# --- HELPER: DOSYA KAYDETME ---
def save_file(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return url_for('static', filename='uploads/' + filename)
    return None

# --- ROTALAR ---

@app.route('/favicon.ico')
def favicon():
    return "", 204

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').lower().strip()
        password = request.form.get('password')
        
        # Yasaklılar
        if username in ['admin', 'dashboard', 'login', 'register', 'favicon.ico', 'static']:
             flash('Bu kullanıcı adı alınamaz.', 'error')
             return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Bu isim zaten alınmış.', 'error')
            return redirect(url_for('register'))
            
        # DÜZELTME: display_name = username olarak ayarlandı.
        new_user = User(
            username=username, 
            password=generate_password_hash(password),
            display_name=username 
        )
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').lower().strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Kullanıcı adı veya şifre hatalı.', 'error')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # 1. Dosya Yüklemeleri (Öncelik: Dosya > Form Linki > Veritabanındaki Eski Link)
        
        # Arka Plan
        bg_file = request.files.get('bg_file')
        bg_text = request.form.get('background_url')
        if bg_file and bg_file.filename != '':
            current_user.background_url = save_file(bg_file)
        elif bg_text and bg_text.strip() != '':
            current_user.background_url = bg_text

        # Avatar
        av_file = request.files.get('avatar_file')
        av_text = request.form.get('profile_pic_url')
        if av_file and av_file.filename != '':
            current_user.profile_pic_url = save_file(av_file)
        elif av_text and av_text.strip() != '':
            current_user.profile_pic_url = av_text
        
        # Ses
        au_file = request.files.get('audio_file')
        au_text = request.form.get('audio_url')
        if au_file and au_file.filename != '':
            current_user.audio_url = save_file(au_file)
        elif au_text and au_text.strip() != '':
            current_user.audio_url = au_text

        # 2. Metin Alanları
        current_user.display_name = request.form.get('display_name')
        current_user.description = request.form.get('description')
        current_user.location = request.form.get('location')
        
        # 3. Görünüm & Renk
        current_user.profile_opacity = request.form.get('profile_opacity')
        current_user.profile_blur = request.form.get('profile_blur')
        current_user.accent_color = request.form.get('accent_color')
        current_user.text_color = request.form.get('text_color')
        current_user.bg_color = request.form.get('bg_color')
        current_user.icon_color = request.form.get('icon_color')
        
        # 4. Switchler
        current_user.monochrome_icons = 'monochrome_icons' in request.form
        current_user.animated_title = 'animated_title' in request.form
        current_user.badge_glow = 'badge_glow' in request.form
        current_user.discord_rpc = 'discord_rpc' in request.form
        
        # 5. Sosyal Medya
        current_user.discord = request.form.get('discord')
        current_user.instagram = request.form.get('instagram')
        current_user.youtube = request.form.get('youtube')
        current_user.spotify = request.form.get('spotify')
        current_user.telegram = request.form.get('telegram')
        current_user.tiktok = request.form.get('tiktok')
        current_user.twitter = request.form.get('twitter')
        
        db.session.commit()
        flash('Profil başarıyla güncellendi!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('dashboard.html', user=current_user)

@app.route('/<username>')
def profile(username):
    if username == "favicon.ico": return "", 404
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
    app.run(debug=True)
