import mysql.connector

class ConnectionError(Exception):
# create an exception handler class here in database context manager module,
# instead of handling the exceptions for view_the_log code block itself, which means
# needing to import the mysql connection and avoiding coupling of backend database.
# we'll add try and except block to protect our __enter__ code block.
# we're passing in the Exception which means all attributes and behaviors...
# of exception is available to Connection Error.
    pass
    # no code needed here. pass.


class UseDatabase: # create class using class keyword and CamelCase style
# to use the "with" statement we need to create a class with:
# 1) __init__ method to perform initialization(optional)
# 2) __enter__ method to do any setup
# 3) __exit__ method to any teardown
# or just use the contextlib standard library
# adding self to conn and cursor in __enter__ method ensures that ...
# both attributes are available to the whole class.
    def __init__(self, config: dict) -> None: # annotation indicates...
        # method returns none, accepts one argument -> config which is a dict.
        # initiliazing the configuration with attribute config
        self.configuration = config

    def __enter__(self) -> 'cursor': # annotation says this returns a cursor
        # __enter__ method onlt take self as argument.
        # establish connector to the server(note ** on self.configuration)
        try: # protect the code with try.
            self.conn = mysql.connector.connect(**self.configuration)
            # establish cursor to connector
            self.cursor = self.conn.cursor()
            # return the cursor
            return self.cursor
        except mysql.connector.errors.InterfaceError as err:
        # catch the error.
        # use the full name of the backend specific exception (mysql.connector.errors.InterfaceError).
            raise ConnectionError(err)
            # raise the custom exception.
    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        # annotation in method indicates this returns no value
        # exception handlers are passed in as arguments.
        # when something goes wrong the interpreter notifies the __exit__ .
        self.conn.commit() # commit to write the file in database
        self.cursor.close() # close the cursor
        self.conn.close() # close the connector
