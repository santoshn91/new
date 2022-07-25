from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


#Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html",
                           logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form.get('email')).first():
            flash("You've already signed up with this email, log in instead!")
            return redirect(url_for('login'))

        new_user = User(email=request.form.get('email'),
                        name=request.form.get('name'),
                        password=request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        flash("You're Successfully Registred...!")
        return redirect(url_for('login'))
    return render_template("register.html",
                           logged_in=current_user.is_authenticated)


@app.route("/change", methods=["GET", "POST"])
def change():
    if request.method == "POST":
        user_id = current_user.id
        user_pass_is_change = User.query.get(user_id)
        user_pass_is_change.password = request.form["password"]
        db.session.commit()
        return redirect(url_for('logout'))
    return render_template("pass_change.html",
                           logged_in=current_user.is_authenticated)


@app.route('/delete')
def delete():
    d = request.args.get('id')
    btd = User.query.get(d)
    db.session.delete(btd)
    db.session.commit()
    flash("you're account is Deleted!")
    return redirect(url_for('login'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exists, please try again!")
            return redirect(url_for('login'))

        elif user.password != password:
            flash("Password incorrect, please try again!")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('secrets'))

    return render_template("login.html",
                           logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    id = current_user.id
    return render_template("secrets.html",
                           uid=id,
                           name=current_user.name,
                           email=current_user.email,
                           logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
