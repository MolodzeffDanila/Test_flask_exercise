from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import bitly_api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
token = bitly_api.Connection(access_token='cce1b9f2ad0dfc157a138a71dc59a77873d84d7b')


class Table(db.Model):
    ident = db.Column(db.Integer, primary_key=True)
    old_url = db.Column(db.String(500), nullable=False, unique=True)
    new_url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return '<Table %r>' % self.ident


def change_url(old_url):
    new_url = token.shorten(old_url)["url"]
    return new_url


@app.route('/', methods=['POST', 'GET'])
def index():
    elem = ""
    if request.method == "POST":
        input_url = request.form['url_']
        if not input_url:
            error_type_ = "Error"
            error_mess_ = "Empty URL adress, try again."
            return error(error_type_, error_mess_)
        missing = Table.query.filter_by(old_url=input_url).first()
        if missing:
            elem = missing.new_url
        else:
            output_url = change_url(input_url)
            table1 = Table(old_url=input_url, new_url=output_url)
            try:
                db.session.add(table1)
                db.session.commit()
                elem = output_url
            except:
                error("Cannot add article.")
    return render_template("index.html", el=elem)


@app.route('/Error')
def error(error_type, error_mess):
    return render_template("EmptyURL.html", error=error_mess,type=error_type)


@app.route('/post')
def post():
    articles = Table.query.order_by(Table.ident).all()
    return render_template("post.html", articles=articles)


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=False)
