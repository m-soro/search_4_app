from flask import Flask
from vsearch import search_for_letters as sfl


app = Flask(__name__)

@app.route('/')
def hello() -> str:
    return 'Hello world from Flask!'

@app.route('/search4')
def do_search() -> str:
    return str(sfl('alice in wonderland'))

app.run()
