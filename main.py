from service import create_app

app = create_app()

# Stub that allows for running from commandline via python main.py
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    app.run(
        host=app.config.get("HOST"),
        port=app.config.get("PORT"),
        ssl_context=(app.config.get("SSL_CERT"), app.config.get("SSL_KEY")),
    )
