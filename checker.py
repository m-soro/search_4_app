# create a decorator module in 3 steps
# 1) a decorator is just a function
def check_logged_in(func):
    # 2) define a decorated function that accepts another function as...
    #    an argument by referring as an function object( without the "()" ).
    def wrapper():
        # 3) the decorator returns a new function as its return value.
        if 'logged_in' in session: # check if logged_in key is in session dictionary.
            return func()  # invoke the decorated func. The argument in check_logged_in func.
        return 'You are NOT logged in'
return wrapper # return the nested function as function object.
