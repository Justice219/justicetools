# Some imports and local stuff
from website import create_app
app = create_app()

# Lets run the app!
if __name__ == '__main__':
    app.run(debug=True)

