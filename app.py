from flask import Flask, render_template
from vsearch import search_for_letters as sfl


app = Flask(__name__)

@app.route('/')
def hello() -> str:
    return 'Hello world from Flask!'

@app.route('/search4', methods=['POST']) # POST methods notice that in Flask
    # methods is plural. Allows a web browser to send data to the server.
    # The @app.route accepts this as 2nd argument
    # this matches our POST method in the entry.html form section.
def do_search() -> str:
    return str(sfl('alice in wonderland'))

@app.route('/entry') # this creates a new URL to the webapp
def entry_page() -> 'html':
    return render_template('entry.html',
            the_title='Welcome to search for letters website!')
            # ^provides a value to associate with 'the_title' argument
app.run(debug=True) # debug True enables flask to restart the webapp every
                    # time it detects a change.
