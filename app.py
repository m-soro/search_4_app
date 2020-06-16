from flask import Flask, render_template, request
# render_template -> when provided with the name...
# of a template and any required arguments returns a string of html.
# request -> provides us access to posted data from our html form
# it has a dict attribute "form" and just like any old python dict
# it supports bracket notation so we'll get the forms data like this...
# request.form['phrases'] and request.form['letters'].
from vsearch import search_for_letters as sfl

app = Flask(__name__)

@app.route('/search4', methods=['POST']) # POST methods notice that in Flask
    # methods is plural. Allows a web browser to send data to the server.
    # The @app.route accepts this as 2nd argument
    # this matches our POST method in the entry.html form section.
def do_search() -> 'html': # annonating that this function returns html
    phrase = request.form['phrase'] # using the request.form to access...
    letters = request.form['letters'] # the form data.
    title = 'Here are your results:' # assign title
    results = str(sfl(phrase, letters)) # assign results
    return  render_template('results.html', # don't forget the quote marks!
                                the_phrase=phrase,
                                the_letters=letters,
                                the_title=title,
                                the_results=results)
    # render_template is used to provide for the missing arguments in the
    # results.html page which expects four arguments.
@app.route('/') # the entry_page function now has two associated URL's!
@app.route('/entry') # this creates a new URL to the webapp
def entry_page() -> 'html': # annonating that this function returns html
    return render_template('entry.html',
            the_title='Welcome to search for letters website!')
            # ^provides a value to associate with 'the_title' argument.
app.run(debug=True) # debug True enables flask to restart the webapp every
                    # time it detects a change.
