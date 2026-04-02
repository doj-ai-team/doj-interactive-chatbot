import sys
import os

# Add the project dir to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def test_roles():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        # Create a basic Citizen
        user = User(username='testcit', email='c@test.com', role='Citizen')
        user.set_password('123')
        db.session.add(user)
        db.session.commit()
    
    with app.test_client() as client:
        # Login
        response = client.post('/auth/login', json={
            'email': 'c@test.com',
            'password': '123'
        }, headers={'Accept': 'application/json'})
        
        print("Login status:", response.status_code)
        
        # Test predict with Citizen role
        res = client.get('/predict')
        print("/predict Status Code:", res.status_code)
        if res.status_code == 403:
            print("Access correctly denied to Citizen for /predict")
        else:
            print("Vulnerability! Citizen accessed /predict. Code:", res.status_code)

if __name__ == '__main__':
    test_roles()
