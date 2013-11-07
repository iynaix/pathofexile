from flask import Flask
from flask import render_template
from dump import search_items
app = Flask(__name__)


@app.route('/')
def search_results():
    return render_template('items.html', items=search_items())

if __name__ == '__main__':
    app.run(debug=True)
