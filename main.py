from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from signin import login_bp
from projects import project_blueprint
from get_project import get_project

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Secret key for session management

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

app.register_blueprint(login_bp)
app.register_blueprint(project_blueprint)
app.register_blueprint(get_project)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
