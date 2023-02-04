Getting Started:
    1. Setup virtual environment and activate it (see https://docs.python.org/3/library/venv.html)
    2. Install external modules 
        $ pip install -r requirements.txt
    3. run app:
        $ ./api.py
    4. create and copy .env file (in the discord)

    **Notes**
    When installing any new external modules via pip, run:
        $ pip freeze > requirements.txt
        
    Running Tests:
        $ python3 -m unittest <testfilename.py>