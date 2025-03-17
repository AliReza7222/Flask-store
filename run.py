from store.app import create_app
from store.settings import DEBUG

app = create_app()

if __name__ == "__main__":
    app.run(debug=DEBUG)
