from flask import current_app as app


# Add a route for the 'home' page
# use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def hello_world():
    # The function returns the message we want to display in the user’s browser. The default content type is HTML,
    # so HTML in the string will be rendered by the browser.
    return 'Hello World!'
