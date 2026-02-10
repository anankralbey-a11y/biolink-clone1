from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# --- AYARLAR ---
# Buraya klavyeden rastgele uzun bir şey sallasan da olur
app.config['SECRET_KEY'] = 'bunu-kimse-tahmin-edemez-xs823-rastgele-yazi' 

# Render'da veritabanı dosyasının yolu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Veritabanı Modelleri ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    # Profil Özellikleri
    display_name = db.Column(db.String(50), default="Kullanıcı")
    bio = db.Column(db.String(200), default="Henüz bir bio eklenmedi.")
    background_url = db.Column(db.String(500), default="https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif")
    profile_pic_url = db.Column(db.String(500), default="https://cdn.discordapp.com/embed/avatars/0.png")
    music_url = db.Column(db.String(500), default="") 
    discord_link = db.Column(db.String(200), default="")
    instagram_link = db.Column(db.String(200), default="")
    view_count = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ÖNEMLİ: Tabloları Render'da oluşturmak için bu kod burada olmalı ---
with app.app_context():
    db.create_all()

# --- Route'lar (Sayfalar) ---

# Favicon hatasını önlemek için boş döndüren kod
@app.route('/favicon.ico')
def favicon():
    return "", 204

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        
        # Kullanıcı adı kontrolü
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Bu kullanıcı adı zaten alınmış!', 'error')
            return redirect(url_for('register'))
            
        # Yasaklı kelimeler (sistem dosyaları vb.)
        if username in ['admin', 'dashboard', 'login', 'register', 'logout', 'favicon.ico']:
             flash('Bu kullanıcı adını alamazsın.', 'error')
             return redirect(url_for('register'))

        new_user = User(username=username, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Hatalı kullanıcı adı veya şifre.', 'error')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        current_user.display_name = request.form.get('display_name')
        current_user.bio = request.form.get('bio')
        current_user.background_url = request.form.get('background_url')
        current_user.profile_pic_url = request.form.get('profile_pic_url')
        current_user.music_url = request.form.get('music_url')
        current_user.discord_link = request.form.get('discord_link')
        current_user.instagram_link = request.form.get('instagram_link')
        
        db.session.commit()
        flash('Profil güncellendi!', 'success')
        
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/<username>')
def profile(username):
    # Favicon isteği buraya düşerse yoksay
    if username == "favicon.ico":
        return "", 404

    user = User.query.filter_by(username=username.lower()).first()
    if not user:
        return "Kullanıcı bulunamadı", 404
    
    # Görüntülenme sayısını artır
    user.view_count += 1
    db.session.commit()
    
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
