# run.py

from dotenv import load_dotenv

# create_app() 보다 먼저 실행되어야 합니다.
load_dotenv() 

from src import create_app

app = create_app()

if __name__ == '__main__':
    app.config['DEBUG'] = False
    app.run()
