# Testing the Flask app

Use `test.py` just to test the wrapping code without using Flask.

To test this using a Flask server you run the app as a service in one terminal:

```bash
$ python app.py
```

And poke at it from another:

```bahs
$ curl -i -H "Accept: application/json" -X PUT -d@example-mmif.json http://0.0.0.0:5000/
```

This needs miff-python version 0.2.0 and not 0.2.0.dev10 because with the latter you get validation errors.

