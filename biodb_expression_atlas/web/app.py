from flask_cors import CORS
import connexion
import webbrowser


application = connexion.FlaskApp(__name__)
application.add_api('openapi.yaml')

CORS(application.app)


def run(port: int, debug_mode: bool, open_browser: bool):
    url = f'http://127.0.0.1:{port}/ui'
    if open_browser:
        webbrowser.open(url)
    print(f'starting web server {url}')
    application.run(host='0.0.0.0', port=port, debug=debug_mode)

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=False)