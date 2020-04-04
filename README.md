# Rifmuj!

This will be a Russian rhyme dictionary. 

## Requirements

* Python 3.7 or later
* TypeScript
* Flask
* Sqlalchemy

## Making it work

Install the requirements.

```bash
pip install -r requirements.txt
sudo apt install node-typescript
```

* Generate JavaScript code from the TypeScript source.

```bash
tsc
```

* Download the dictionary source file and put it into the `data` folder.

<https://drive.google.com/file/d/1fSy3TUcsM0iFull1v9dW_FkK06ex7MH9>


* Generate the DB from this file.

```bash
python3 data/db_generation.py
```

* After that, just run the web app.

```bash
./run.sh
```
(on Windows cmd, use `run.bat` instead)

* Open <http://127.0.0.1:5000/>

## Testing

We use `mypy` for typechecking and `pytest` for testing.
