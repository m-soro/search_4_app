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
    """log details of web request and the result"""
    # 3)establish connection to server, using "connect(pass here the connection dictionary)"
    #   3.a) the ** on connection dictionary expands the dictionary to four single arguments.
    conn = mysql.connector.connect(**dbconfig)

    # 4)open a cursor whhich allows us to send sql commands and receive results.
    cursor = conn.cursor()

    # 5)assign the sql command to _SQL variable using insert command.
    #   5.a)note that when using cursor.execute using insert query, the data
    #       will be in cache and will be waiting to be written.
    #   5.b)use conn.commit method to force write all cached data.
    _SQL = """insert into log
              (phrase, letters, ip, browser_string, results)
              values
              (%s, %s, %s, %s, %s)""" # %s acts as placeholders.
    cursor.execute(_SQL, (req.form['phrase'],
                          req.form['letters'],
                          req.remote_addr,
                          req.user_agent.browser,
                          res,))
    conn.commit() # force write cached data
    cursor.close() # close cursor
    conn.close() # close connector
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
def view_the_log() -> 'html': # funtion returns a html
    contents = [] # create a new empty list
    with open('search.log') as log: # reads the file and assigns the file stream to 'log'
        for line in log: # loop thru each line in the log files stream
            contents.append([]) # append new empty list to 'contents'
            for item in line.split('||'): # split the line, then process each item ...
                contents[-1].append(escape(item)) # in the resulting split list then append.
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results') # table titles
    return render_template('viewlog.html', # call render_template in viewlog.html
                            the_title='View Log', # provide arguments to viewlog.html
                            the_row_titles=titles,
                            the_data=contents)
    # return str(contents) <- removed
    # contents = log.readlines() <- removed read all the lines of log data into a list
    # return escape(''.join(contents))<- removed takes the list of strings and join
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
