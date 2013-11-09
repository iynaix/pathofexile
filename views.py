from app import app, db
from models import Item, Requirement
from flask import render_template

def search_items():
    #items with levels
    # Item.query.join(Item.requirements).filter(
    #     Item.requirements.any(name="Level")
    # ).order_by(Requirement.value).all()
    return Item.query.join(Item.requirements).filter(
        Item.properties.any(name="Experience")
    ).all()

@app.route('/')
def search_results():
    return render_template('items.html', items=list(search_items()))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
