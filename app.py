from flask import Flask, render_template, request, escape, session, copy_current_request_context
# render_template -> when provided with the name...
# of a template and any required arguments returns a string of html.
# request -> provides us access to posted data from our html form
# it has a dict attribute "form" and just like any old python dict
# it supports bracket notation so we'll get the forms data like this...
# request.form['phrases'] and request.form['letters'].
# escape -> needed to translate html markup from the view_the_log function
# copy_current_request_context -> ensures that we have a copy of the created request context...
#                                  and will be available when the function is called.
from vsearch import search_for_letters as sfl

from checker import check_logged_in
# imported checker library which checks if user is log in or logged out.

from threading import Thread
# imported the threading library to use Thread to run our code concurrently.

# from time import sleep # used to simulate slow connection.

from db_context_mgr import UseDatabase, ConnectionError, CredentialsError, SQLError
 # imported our context manager module, we have four classes that we created...
 # 1) UseDatabase   2)ConnectionError   3)CredentialsError  4) SQLError

app = Flask(__name__)

# app.config is a built in configuration in Flask, a dict that...
# you can add values and keys as needed.
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
# 8)to check sql table
#   8.a)refer to step 1.1.c
#   8.b)type -> use 'subDataBaseName'
#   8.c)type -> show tables;
#   8.d)type -> select * from 'subTableName'
# 9)delete from table
#   9.a)clear all data from table -> truncate table 'subTableName'
#   9.b)delete specific rows -> delete from log where id in (124,123);
# 10)to exit -> quit

# use mysql querries to answer database related questions...
# 1) how many requests have been responded to?
    # 1.1) select * from log;
# 2) what's the most common list of letters?
    # 2.1) select count(*) from log;
# 3) what's the most common list of leters?
    # 3.1) select count(letters) as 'count', letters from log
    #      group by Letters
    #      order by count desc
    #      limit 1;
# 4) which browser is being used the most?
    # 4.1) select browser_string, count(browser_string) as 'count' from log
    #      group by browser_string
    #      order by count desc
    #      limit 1;

# protecting codes using try/except blocks using classes in db_context_mgr module.:
# 1) do_search -> interacts w/ database so we added a try/except block to handle exceptions and...
#              -> nested inside is the log_request which writes on our back end database.
# 2) view_the_log -> interacts w/ database as well, however Flask invokes this code not us...
#                    which means we'll define this exception handler inside the db_context_mgr module
#                    and to avoid coupling of our code to back end database.
#                 -> Here we're guarding for:
#                               InterfaceError w/c is database connection error and ...
#                               ProgrammingError w/c occurs in incorrect SQL querry or...
#                                                incorrect credentials.

@app.route('/search4', methods=['POST']) # POST methods notice that in Flask
# methods is plural. Allows a web browser to send data to the server.
# The @app.route accepts this as 2nd argument
# this matches our POST method in the entry.html form section.
def do_search() -> 'html': # annonating that this function returns html
    """retrieves the request from web which will be passed to
        log request function to be written in database"""
    phrase = request.form['phrase'] # using the request.form to access...
    letters = request.form['letters'] # the form data.
    title = 'Here are your results:' # assign title on results.html page.
    results = str(sfl(phrase, letters)) # assign results in string type.
    try:
        @copy_current_request_context # -> ensures that HTTP request remains active even....
                                      # after a function is subsequently executed in thread.
        def log_request(req: 'flask_request', res: str) -> None: # moved from the top.
            """log details of web request and the results."""
            # use the "with" together w/ UseDatabase passing in the app.config as cursor
            # sleep(15) # mimicking slow interaction to database.
            with UseDatabase(app.config['dbconfig']) as cursor:
                    _SQL = """insert into log
                    (phrase, letters, ip, browser_string, results)
                    values
                    (%s, %s, %s, %s, %s)""" # %s acts as placeholders.
                    cursor.execute(_SQL, (req.form['phrase'],
                                    req.form['letters'],
                                    req.remote_addr,
                                    req.user_agent.browser,
                                    res,))
    except Exception as err:
          print(f'*-*-*-*-*-* Logging exception with this error: {(str(err))} *-*-*-*-*-*')

    try: # protecting this block of code in case connection to database is unavailable.
        t = Thread(target=log_request, args=(request,results))
        # wrapping log_request function in Thread object to avoid waiting for writing...
        # in database.
        t.start()
        # calling the log_request function.
    except Exception as err: # a catch-all exception, print exception as friendly string.
        print(f'*-*-*-*-*-* Logging exception with this error: {(str(err))} *-*-*-*-*-*')
    # render_template is used to provide for the missing arguments in the ...
    # results.html page which expects four arguments.
    return  render_template('results.html', # don't forget the quote marks!
                                the_phrase=phrase,      # 1
                                the_letters=letters,    # 2
                                the_title=title,        # 3
                                the_results=results)    # 4

@app.route('/') # the entry_page function now has two associated URL's! ('/') and ('/entry')
@app.route('/entry') # this creates a new URL to the webapp
def entry_page() -> 'html': # annonating that this function returns html
    # render_template is used to provide for the missing argument in the ...
    # entry.html page which expects one argument.
    return render_template('entry.html',
            the_title='Welcome to search for letters website!') # 1

@app.route('/viewlog')
@check_logged_in # check if user is logged in using our created checker module
def view_the_log() -> 'html': # function returns a html
    # instead of reading from the search.log text file, we are using...
    # with UseDatabase(app.config['dbconfig']) as cursor:(which allows...
    # us to send commands and receive results.)
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            # if you run this command in mysql> this displays all the below info.
            _SQL = """select phrase, letters, ip, browser_string, results
                    from log"""
                    # pass the _SQL command to mysql and...
            cursor.execute(_SQL)
            # assign the results to contents using cursor.fetchall()
            # you can ask for results from the cursor in 3 ways:
            # 1) cursor.fetchone() -> retrieves a sinle row of results.
            # 2) cursor.fetchmany() -> retrieves the number of row you specified.
            # 3) cursor.fetchall() -> retrieves all the rows that make up the results.
            contents = cursor.fetchall()
            # ammended to include the phrase and letters instead of just one column -> form
            titles = ('Phrase','Letters','Remote_addr','User_agent','Results')
            # render_template is used to provide for the missing arguments in the ...
            # viewlog.html page which expects three arguments.
            return render_template('viewlog.html',
                                    the_title='View Log',        # 1
                                    the_row_titles=titles,       # 2
                                    the_data=contents,)          # 3


    except ConnectionError as err:
        # in ConnectionError we specifically instructed the exception handler...
        # to look for InterfaceError which occurs when connection to database fails.
        print(f'*-*-*-*-*-* Did check your database connection? {str(err)}*-*-*-*-*-*')
        # print our error message for our internal error message.
    except CredentialsError as err:
        # in CredentialsError we specifically instructed the exception handler...
        # to look for ProgrammingError which occurs when database credentials are incorrect.
        print(f'*-*-*-*-*-* Did you check your username and password? {str(err)}*-*-*-*-*-*')
        # print our error message for our internal error message.
    except SQLError as err:
        # in SQLError we specifically instructed the exception handler...
        # to look for ProgrammingError which occurs when SQL commands has errors.
        print(f'*-*-*-*-*-* Is your qerry correct?  {str(err)}*-*-*-*-*-*')
        # print our error message for our internal error message.
    except Exception as err:
        # let's also define the catch-all exception and...
        print(f'*-*-*-*-*-* Logging this error as: {str(err)}*-*-*-*-*-*')
        # print our error message for our internal error message
    return render_template('viewlog.html',
                        error_mess = 'Oops... Something\'s gone wrong...')
        # return the visible part of the error message instead of the...
        # scary looking error message.

@app.route('/login')
def do_login():
    session['logged_in'] = True
    # we are setting the session's dictionary key which is 'logged_in' to True
    return render_template('login.html',
                            the_message="You are now logged IN.")
    # return a message to confirm we're logged IN.

@app.route('/logout')
def do_logout():
    del session['logged_in']
    # the recommended way of logging out is removing the key instead of ...
    # just setting the key to True.
    return render_template('logout.html',
                            the_message="You are now logged OUT.")
    # return a message to confirm we're logged OUT.

app.secret_key = 'anotherhardtoguesskey'

if __name__ == '__main__':
    app.run(debug=True)
    # wrapping the app.run in dunder name dunder main...
    # let's us execute the code locally, and ...
    # prevents us from having two versions of the code...
    # because in deployment, app.run() will prevent the code from running...
                    # debug True enables flask to restart the webapp every
                    # time it detects a change.
