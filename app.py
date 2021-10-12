from flask import Flask

app = Flask(__name__)

from api.index import view_func as index

app.add_url_rule('/api', 'index', index)

if __name__ == '__main__':
    app.run()
