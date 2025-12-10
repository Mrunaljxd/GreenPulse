from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os, random

# ---------------------------------------------------
# BASIC SETUP
# ---------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greenpulse.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

POINT_TO_INR_RATE = 10  # 10 points = 1 INR

# ---------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)
    role = db.Column(db.String(20), default="user")

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scientific = db.Column(db.String(120))
    difficulty = db.Column(db.String(20))
    base_points = db.Column(db.Integer, default=10)
    description = db.Column(db.Text)

class UserPlant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=True)
    custom_name = db.Column(db.String(100), nullable=True)
    photo = db.Column(db.String(200))
    verified = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="submissions")
    plant = db.relationship("Plant", backref="submissions")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# small helper to compute uploads for current user or admin
def _get_uploads_for_dashboard():
    if current_user.role != 'admin':
        return UserPlant.query.filter_by(user_id=current_user.id).all()
    else:
        return UserPlant.query.filter_by(verified=False, rejected=False).all()

# ---------------------------------------------------
# HOME PAGE
# ---------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for('signup'))

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please login.")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password_input):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash("Incorrect username or password")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    plants = Plant.query.all()
    uploads = _get_uploads_for_dashboard()
    # if a navbar search used the GET /search redirect we might pass search_info from there;
    # normal dashboard loads with no search_info
    search_info = None
    return render_template('dashboard.html', plants=plants, uploads=uploads, search_info=search_info)

# ---------------------------------------------------
# NAVBAR SEARCH (so GET /search doesn't 404)
# This returns the dashboard with search result embedded in the template
# ---------------------------------------------------
@app.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    if not q:
        flash("Please enter a search term.")
        return redirect(url_for('dashboard'))

    # find plant (case-insensitive)
    plant = Plant.query.filter(Plant.name.ilike(f"%{q}%")).first()
    if plant:
        info = {
            "title": plant.name,
            "description": plant.description or "No description available.",
            "care": "Water moderately. Provide sunlight. Fertilize monthly."
        }
    else:
        # fallback/mock info
        info = {
            "title": q.title(),
            "description": f"{q.title()} is a wonderful plant known for its beauty and benefits.",
            "care": "Water moderately. Provide sunlight. Fertilize monthly."
        }

    plants = Plant.query.all()
    uploads = _get_uploads_for_dashboard()
    # pass search_info to template — dashboard.html can display it if present
    return render_template('dashboard.html', plants=plants, uploads=uploads, search_info=info, q=q)

# ---------------------------------------------------
# PLANT SEARCH API (AJAX used by dashboard JS)
# ---------------------------------------------------
@app.route('/get_plant_info', methods=['POST'])
@login_required
def get_plant_info():
    # accept both JSON (fetch) and form-encoded (just in case)
    data = request.get_json(silent=True)
    if data is None:
        data = request.form.to_dict()
    plant_name = (data.get('plant_name') or '').strip()
    if not plant_name:
        return jsonify({"error": "No plant name provided"}), 400

    plant = Plant.query.filter(Plant.name.ilike(f"%{plant_name}%")).first()
    if plant:
        info = {
            "title": plant.name,
            "description": plant.description or "No description available.",
            "care": "Water moderately. Provide sunlight. Fertilize monthly."
        }
    else:
        info = {
            "title": plant_name.title(),
            "description": f"{plant_name.title()} is a wonderful plant known for its beauty and benefits.",
            "care": "Water moderately. Provide sunlight. Fertilize monthly."
        }
    return jsonify(info)

# ---------------------------------------------------
# UPLOAD CUSTOM PLANT PHOTO
# ---------------------------------------------------
@app.route('/upload_custom', methods=['POST'])
@login_required
def upload_custom():
    file = request.files.get('plant-photo')
    plant_name = request.form.get('plant-name', '').strip()

    if not file or not plant_name:
        flash("Please provide a plant name and image.")
        return redirect(url_for('dashboard'))

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    entry = UserPlant(
        user_id=current_user.id,
        plant_id=None,
        custom_name=plant_name.title(),
        photo=filename
    )
    db.session.add(entry)
    db.session.commit()

    flash("Image submitted! Waiting for admin verification.")
    return redirect(url_for('dashboard'))

# ---------------------------------------------------
# IMAGE UPLOAD (EXISTING PLANTS)
# ---------------------------------------------------
@app.route('/upload/<int:plant_id>', methods=['POST'])
@login_required
def upload(plant_id):
    file = request.files.get('photo')

    if not file:
        flash("No image uploaded.")
        return redirect(url_for('dashboard'))

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    entry = UserPlant(user_id=current_user.id, plant_id=plant_id, photo=filename)
    db.session.add(entry)
    db.session.commit()

    flash("Image submitted! Waiting for admin verification.")
    return redirect(url_for('dashboard'))

# ---------------------------------------------------
# WALLET / BALANCE
# ---------------------------------------------------
@app.route('/balance')
@login_required
def balance():
    points = current_user.points
    inr = points / POINT_TO_INR_RATE
    payout = inr * 0.20
    return render_template('balance.html', points=points, inr=inr, payout=payout)

# ---------------------------------------------------
# ADMIN: VERIFY UPLOADS
# ---------------------------------------------------
@app.route('/admin/verify')
@login_required
def admin_verify():
    if current_user.role != "admin":
        return "Access denied."

    submissions = UserPlant.query.filter_by(verified=False, rejected=False).all()
    return render_template("admin_verify.html", uploads=submissions)

@app.route('/admin/approve/<int:entry_id>', methods=['POST'])
@login_required
def approve(entry_id):
    if current_user.role != "admin":
        return "Access denied."

    entry = UserPlant.query.get(entry_id)
    if not entry:
        flash("Entry not found.")
        return redirect(url_for('admin_verify'))

    entry.user.points += entry.plant.base_points if entry.plant else 10
    entry.verified = True
    entry.rejected = False
    db.session.commit()
    flash("Approved!")
    return redirect(url_for('admin_verify'))

@app.route('/admin/reject/<int:entry_id>', methods=['POST'])
@login_required
def reject(entry_id):
    if current_user.role != "admin":
        return "Access denied."

    entry = UserPlant.query.get(entry_id)
    if not entry:
        flash("Entry not found.")
        return redirect(url_for('admin_verify'))

    entry.rejected = True
    entry.verified = False
    db.session.commit()
    flash("Rejected!")
    return redirect(url_for('admin_verify'))

# ---------------------------------------------------
# LEADERBOARD
# ---------------------------------------------------
@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.points.desc()).all()
    return render_template('leaderboard.html', users=users)

# ---------------------------------------------------
# SERVING UPLOADED IMAGES
# ---------------------------------------------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------------------------------------------
# RUN APP
# ---------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        db.create_all()

    app.run(debug=True)



