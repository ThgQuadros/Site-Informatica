from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "sua-chave-secreta-aqui"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site_ti.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

#----- Modelo de Usuário -----
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

#----- Modelo de Mensagem de Contato -----
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#--- Rotas Públicas ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sobre")
def about():
    return render_template("about.html")

@app.route("/areas")
def areas():
    areas_list = [
        {"título": "Redes", "descricao": "Infraestrutura, conectividade e segurança de redes."},
        {"título": "Suporte Técnico", "descricao": "Atendimento e manutenção de sistemas."},
        {"título": "Segurança da Informação", "descricao": "Proteção de dados e prevenção de ataques."},
        {"título": "Cloud Computing", "descricao": "Serviços em nuvem para escalabilidade."},
        {"título": "Desenvolvimento", "descricao": "Criação de Softwares e aplicação web/mobile."},
        {"título": "Data Science", "descricao": "Análise de dados para tomada de decisões."},
    ]
    return render_template("areas.html", areas=areas_list)

@app.route("/contato", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        if name and email and message:
            msg = ContactMessage(name=name, email=email, message=message)
            db.session.add(msg)
            db.session.commit()
            flash("Mensagem enviada com sucesso!", "success")
            return redirect(url_for("contact"))
        else:
            flash("Preencha todos os campos.", "error")
    return render_template("contact.html")

#--- Rotas de Autenticação ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("E-mail ou senha inválidos.", "error")
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password != confirm:
            flash("As senhas não coincidem.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "error")
            return render_template("register.html")

        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Conta criada! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado.", "success")
    return redirect(url_for("home"))

#--- Rotas Protegidas ---
@app.route("/dashboard")
@login_required
def dashboard():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    users_count = User.query.count()
    messages_count = ContactMessage.query.count()
    return render_template("dashboard.html", messages=messages, users_count=users_count, messages_count=messages_count)

#--- Inicialização ---
def create_app():
    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    create_app()
    app.run(debug=True)
