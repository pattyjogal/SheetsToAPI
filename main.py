import dicttoxml
import os
import pyrebase
from xml.dom.minidom import parseString
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# FIREBASE CONFIG
# (Same as in script.py; feel free to copy it over)
config = {
    'apiKey': '',
    'authDomain': '<YOUR_PROJECT_ID_HERE>.firebaseapp.com',
    'databaseURL': 'https://<YOUR_PROJECT_ID_HERE>.firebaseio.com/',
    'storageBucket': '<YOUR_PROJECT_ID_HERE>.appspot.com',
    'serviceAccount': os.path.dirname(os.path.realpath(__file__)) + '/service_auth.json'
}

firebase = pyrebase.initialize_app(config)

# I'd recommend changing `foo` to something more descriptive of your sheets
@app.route("/api/<string:foo>")
def get_item(foo):
    db = firebase.database()
    # This holds the values to return
    vals = []
    if not db.child(foo).get():
        # This means there was an invalid db child name passed
        response = jsonify({'code': 404, 'message': '{} is not a valid database child!'.format(foo)})
        response.status_code = 404
        return response
    try:
        # If you wish to add additional query parameters, do so here in an 'if' statement before the
        # else statement. To learn how to add, check the pyrebase repo for docs:
        # https://github.com/thisbejim/Pyrebase
        # NOTE: If you want to do any `order_by` calls, or any indexing at all on a Firebase DB,
        # you need to explicitly define a `indexOn` rule in your DB's config. For example,
        # "cars": {
        #     ".indexOn": ["model", "color"]
        #   }

        # Now I can write a clause like this to only show cars of a specified model GET parameter:
        # if request.args.get('model'):
        #     vals.extend([v for k,v in db.child(foo)
        #                             .order_by_child('model')
        #                             .equal_to(request.args.get('model'))
        #                             .get().val().items()])

        # (This could be invoked with: "http://example.com/api/cars?model=Honda")

        #else:
        vals = [v for k,v in db.child(sport_name).get().val().items()]
    except IndexError:
        # This means that the supplied parameter value returned no match in the databse
        response = jsonify({'code': 404, 'message': 'The param passed might not exist; check your spelling!'})
        response.status_code = 404
        return response
    # If the user wants XML in return, they can specify it through the format param.
    if request.args.get('format') == 'xml':
        return parseString(dicttoxml.dicttoxml(vals, item_func=lambda x: 'game')).toprettyxml()
    # Otherwise, JSON is implicit, and is returned.
    return jsonify(vals)

if __name__ == '__main__':
    app.run(debug=False)