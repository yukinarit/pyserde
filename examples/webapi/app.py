from flask import Flask, Response, request

from serde import serde
from serde.json import from_json, to_json


@serde
class ToDo:
    id: int
    title: str
    description: str
    done: bool


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/todos', methods=['GET', 'POST'])
def todos():
    print(request.method)
    if request.method == 'GET':
        body = to_json([ToDo(1, 'Play games', 'Play 聖剣伝説3', False)])
        return Response(body, mimetype='application/json')
    else:
        todo = from_json(ToDo, request.get_data())
        return f'A new ToDo {todo} successfully created.'


if __name__ == '__main__':
    app.run(debug=True)
