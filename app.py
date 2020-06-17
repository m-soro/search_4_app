from flask import Flask, render_template, request, escape
# render_template -> when provided with the name...
# of a template and any required arguments returns a string of html.
# request -> provides us access to posted data from our html form
# it has a dict attribute "form" and just like any old python dict
# it supports bracket notation so we'll get the forms data like this...
# request.form['phrases'] and request.form['letters'].
# escape -> needed to translate html markup from the view_the_log function
from vsearch import search_for_letters as sfl

app = Flask(__name__)

def log_request(req: 'flask_request', res: str) -> None:
    # takes two arguments req and res, req is flask request, res is a string
    # and this function returns none.
    with open('search.log', 'a') as log:
            print(req.form, req.remote_addr, req.user_agent, res, file=log, sep='||')
    # this function allows us to write to 'search.log' file using...
    # print() supplied with req, res and file=log as arguments.
    # req is the current assigned Flask object request, which is...
    # the request.form['phrase'] and request.form['letters']
    # res if the result of str(sfl(phrase,letters)).
    # then to invoke this function we'll add this to the do_search function.
    # at the moment, the req is logging our request at object level...
    # we are going to debug by passing the req to dir dir(req)...
    # dir will produce a list and pass it to str to stringfy and then...
    # save to logged file together with res.
    # after running dir we picked up 3 things that we'll want to add to log
    # 1)req.form-> data posted from HTML form, ...
    # 2)req.remote_addr-> the IP address of the web browser running on.
    # 3)req.user_agent -> the identity of the browser posting the data.
    # removed and replaced with one line print statement -
    # instead of print(req.form, file=log) which will produce...
    # extra new lines will pick a '||' as a delimiter using the end='||' attribute
    # ^removed and replaced with one line print statement^
    #we'll add this three new objects to the log_request function.
@app.route('/search4', methods=['POST']) # POST methods notice that in Flask
    # methods is plural. Allows a web browser to send data to the server.
    # The @app.route accepts this as 2nd argument
    # this matches our POST method in the entry.html form section.
def do_search() -> 'html': # annonating that this function returns html
    phrase = request.form['phrase'] # using the request.form to access...
    letters = request.form['letters'] # the form data.
    title = 'Here are your results:' # assign title
    results = str(sfl(phrase, letters)) # assign results
    log_request(request,results) # calling the log_request function.
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
@app.route('/viewlog')
def view_the_log() -> str: # will enable us to view the log, returns a string
    with open('search.log') as log: # this opens/closes and reads the log
        contents = log.readlines() # read all the lines of log data into a list
    return escape(''.join(contents)) # takes the list of strings and join    
         # contents = log.read() <-removed the read method returns the entire contents
         # return escape(contents) <-removed of the file "in one go".
        # enlosed the returned contents in escape to translate our markups


if __name__ == '__main__':
    app.run(debug=True)
    # wrapping the app.run in dunder name dunder main...
    # let's us execute the code locally, and ...
    # we prevents us from having two versions of the code...
    # because in deployment, app.run() will prevent the code from running...
                    # debug True enables flask to restart the webapp every
                    # time it detects a change.
