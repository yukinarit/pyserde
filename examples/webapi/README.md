# WebAPI example

## Run

```
poetry install
poetry run python app.py
```

## Usage

* Get all ToDos
    ```
    $ curl http://localhost:5000/todos
    [{"id": 1, "title": "Play games", "description": "Play 聖剣伝説3", "done": false}]⏎
    ```

* Post a new ToDo
    ```
    $ curl -X POST http://localhost:5000/todos -d '{"id": 1, "title": "Play games", "description": "Play 聖剣伝説3", "done": false}'
    A new ToDo ToDo(id=1, title='Play games', description='Play 聖剣伝説3', done=False) successfully created.⏎
    ```
