from flask import Flask, render_template, request, escape
# render_template -> when provided with the name...
# of a template and any required arguments returns a string of html.
# request -> provides us access to posted data from our html form
# it has a dict attribute "form" and just like any old python dict
# it supports bracket notation so we'll get the forms data like this...
# request.form['phrases'] and request.form['letters'].
# escape -> needed to translate html markup from the view_the_log function
from vsearch import search_for_letters as sfl

from db_context_mgr import UseDatabase # imported our context manager module.

app = Flask(__name__)

# app.config is a built in configuration in Flask a dict that you can add values
# and keys as needed.
app.config['dbconfig'] = {'host':'127.0.0.1', # 1)IP address/"host" running MySQL
                          'user':'searchuser', # 2)user ID to use
                          'password':'searchuserpwd', # 3)pwd asscociated with user ID to use
                          'database':'searchlogDB',} # 4)database on interact with.
# mySQL how to's
# 1)enter mysql -> /usr/local/mysql -u root -p
#   1.a)you will see "mysql>"
#   1.b)always end all mysql command with ";"
#   1.c)if mysql login has already been created -> /usr/local/mysql/bin/mysql -u 'subUserName' -p *press enter then type* 'subPwd'
# 2)create database -> create database 'subDataBaseName'
# 3)create userID and pwd -> create user 'subUserName' identified by 'subPwd'
# 4)grant permission to access db -> grant all priviledges on subDataBaseName.* to 'subUserName'
# 5)use the database -> use 'subDataBaseName'
# 6)to create the table:
#   6.a) create table 'subTableName' (
#   6.b) -> id int auto_increment primary key,
#   6.c) -> ts timestamp default current_timestamp,
#   6.d) -> phrase varchar(128) not null,
#   6.e) -> letters varchar(32) not null,
#   6.f) -> ip varchar(16) not null,
#   6.g) -> browser_string varchar(256) not null,
#   6.h) -> results varchar(64) not null );
# 7)confirm the created table -> describe log;
# 8)to exit -> quit

# 1)import the database driver, makes the MySQL-specific driver available to Python's DB-API.
def log_request(req: 'flask_request', res: str) -> None:
    """log details of web request and the results."""

    with UseDatabase(app.config['dbconfig']) as cursor:
    # use the "with" together w/ UseDatabase passing in the app.config as cursor
        _SQL = """insert into log
              (phrase, letters, ip, browser_string, results)
              values
              (%s, %s, %s, %s, %s)""" # %s acts as placeholders.
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res,))
    # conn.commit() # force write cached data -> not needed we have __exit__
    # cursor.close() # close cursor -> not needed we have __exit__
    # conn.close() # close connector -> not needed we have __exit__
    # 6)to check sql table
    #   6.a)refer to step 1.1.c
    #   6.b)type -> use 'subDataBaseName'
    #   6.c)type -> select * from 'subTableName'

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
def view_the_log() -> 'html': # function returns a html
    with UseDatabase(app.config['dbconfig']) as cursor:
    # instead of reading from the search.log text file, we are using...
    # with UseDatabase(app.config['dbconfig']) as cursor:(which allows...
    # us to send commands and receive results.)
        _SQL = """select phrase, letters, ip, browser_string, results
                    from log"""
        # if you run this command in mysql> this displays all the above info.
        cursor.execute(_SQL)
        # pass the _SQL command to mysql and...
        contents = cursor.fetchall()
        # assign the results to contents using cursor.fetchall()
        # you can ask for results from the cursor in 3 ways:
            # 1) cursor.fetchone() -> retrieves a sinle row of results.
            # 2) cursor.fetchmany() -> retrieves the number of row you specified.
            # 3) cursor.fetchall() -> retrieves all the rows that make up the results.
    titles = ('Phrase','Letters','Remote_addr','User_agent','Results')
    # ammended to include the phrase and letters instead of just one column -> form
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents,)

if __name__ == '__main__':
    app.run(debug=True)
    # wrapping the app.run in dunder name dunder main...
    # let's us execute the code locally, and ...
    # we prevents us from having two versions of the code...
    # because in deployment, app.run() will prevent the code from running...
                    # debug True enables flask to restart the webapp every
                    # time it detects a change.
