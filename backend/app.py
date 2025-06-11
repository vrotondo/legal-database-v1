from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///legal_cms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models (we'll create these next)
from models import User, Client, Case, Document, TimeEntry

# Your existing API endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'success',
        'message': 'Legal CMS API is running!',
        'version': '1.0.0',
        'database': 'connected'
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'message': 'Hello from your Legal CMS backend!',
        'data': ['Client 1', 'Client 2', 'Client 3']
    })

# New endpoints to test our models
@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        clients = Client.query.all()
        clients_data = [{
            'id': client.id,
            'name': f"{client.first_name} {client.last_name}",
            'email': client.email,
            'phone': client.phone,
            'created_at': client.created_at.isoformat()
        } for client in clients]
        
        return jsonify({
            'status': 'success',
            'clients': clients_data,
            'count': len(clients_data)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/clients', methods=['POST'])
def create_client():
    try:
        data = request.get_json()
        
        new_client = Client(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            zip_code=data.get('zip_code', '')
        )
        
        db.session.add(new_client)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Client created successfully',
            'client': {
                'id': new_client.id,
                'name': f"{new_client.first_name} {new_client.last_name}",
                'email': new_client.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True, port=5000)