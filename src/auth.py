from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import os
from datetime import timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from dotenv import load_dotenv  # ✅ Import dotenv

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Correct CORS setup
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:8000", "http://150.230.138.173:8087"]}},
    supports_credentials=True
)

# ✅ Use environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "Registration successful"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    access_token = create_access_token(identity={"id": user.id, "email": user.email})
    return jsonify({
        "success": True, 
        "token": access_token, 
        "user": {"id": user.id, "email": user.email}
    }), 200

@app.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    current_user = get_jwt_identity()
    return jsonify({"success": True, "user": current_user}), 200

@app.route('/download', methods=['GET', 'OPTIONS'])
@jwt_required()
def download_file():
    """ Secure file download with JWT authentication """
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    file_path = request.args.get('file')
    
    if not file_path:
        return jsonify({"success": False, "message": "File path missing"}), 400

    filename = os.path.basename(file_path)
    safe_path = safe_join("uploads", filename)  # ✅ Prevent directory traversal

    if not os.path.exists(safe_path):
        return jsonify({"success": False, "message": "File not found"}), 404

    response = send_file(safe_path, as_attachment=True)
    response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
