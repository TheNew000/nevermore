from flask import Flask, render_template, redirect
from flaskext.mysql import MySQL
import bcrypt

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
