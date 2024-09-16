import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

DISC = [('DSWA5', 'DSWA5'), ('GPSA5', 'GPSA5'), ('IHCA5', 'IHCA5'), ('SODA5', 'SODA5'), ('PJIA5', 'PJIA5'), ('TCOA5', 'TCOA5')]

class NameForm(FlaskForm):
    disc = SelectField('Disciplina:', choices=DISC, validators=[DataRequired()])
    data_ocorrencia = DateField('Data da ocorrência:', validators=[DataRequired()])
    descricao_ocorrencia = TextAreaField('Descrição da ocorrência:', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

class Disc(db.Model):
    __tablename__ = 'discs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='disc', lazy='dynamic')

    def __repr__(self):
        return '<Disc %r>' % self.name

class Ocor(db.Model):
    __tablename__ = 'ocors'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.datetime)
    descricao = db.Column(db.String(250))
    disc_id = db.Column(db.Integer, db.ForeignKey('discs.id'))

    def __repr__(self):
        return '<Ocor %r>' % self.data

    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    disc_id = db.Column(db.Integer, db.ForeignKey('discs.id'))

    def __repr__(self):
        return '<User %r>' % self.username

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Disc=Disc)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/delete/<username>', methods=['GET', 'POST'])
def delete_user(username):
    # Busca o usuário no banco de dados
    user = User.query.filter_by(username=username).first()

    # Se o usuário existir, remover
    if user:
        db.session.delete(user)
        db.session.commit()
        return f"Usuário {username} foi removido com sucesso."
    else:
        return f"Usuário {username} não encontrado."


@app.route('/professores', methods=['GET', 'POST'])
def professores():
    form = NameForm()
    ocor_all = Ocor.query.all()
    discs = Disc.query.all()
    
    if form.validate_on_submit():
        ocor_disc = Disc(name=form.disc.data)
        db.session.add(ocor_disc)
        db.session.commit()
        ocor = Ocor(date=form.data_ocorrencia.data, disc=ocor_disc, descricao=form.descricao_ocorrencia.data)
        db.session.add(ocor)
        db.session.commit()
        session['data_ocorrencia'] = form.data_ocorrencia.data
        session['disc'] = form.disc.data
        session['descricao_ocorrencia'] = form.descricao_ocorrencia.data
        
        return redirect(url_for('professores'))
    return render_template('professore.html', form=form,
                           ocor_all=ocor_all, discs=discs)


if __name__ == '__main__':
    app.run(debug=True) 
