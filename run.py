# src/run.py
# run.py - 애플리케이션 실행 파일

from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

    