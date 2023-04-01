from App import create_app

generator_log_app = create_app()

if __name__ == "__main__":
    generator_log_app.run(host="127.0.0.1", port=8080, debug=True)