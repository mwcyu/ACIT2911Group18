from flask import session
import numpy as np
import face_recognition
import cv2
import pytest
from unittest.mock import patch, MagicMock

def test_login_page_loads(client):
    res = client.get("/auth/login")
    assert res.status_code == 200
    assert b"Login" in res.data


def test_access_session(client):
    with client:
        client.post("/auth/login", data=
                    {"phone":"778-159-1152",
                        "password":"sun789"
                        })
        assert session["_user_id"] == "2"

def test_request_example(client):
    res = client.get("/")
    assert b"Store" in res.data


@pytest.fixture
def mock_face_recognition():
    with patch('face_recognition.face_locations') as mock_locations:
        with patch('face_recognition.face_encodings') as mock_encodings:
            # Mock face detection
            mock_locations.return_value = [(0, 20, 20, 0)]  # Mock face location
            mock_encodings.return_value = [np.array([0.1, 0.2, 0.3])]  # Mock face encoding
            yield {
                'locations': mock_locations,
                'encodings': mock_encodings
            }

def test_facescan_page_loads(client):
    res = client.get("/auth/facescan")
    assert res.status_code == 200
    assert b"Face Recognition" in res.data


def test_facescan_page_register_mode(client):
    res = client.get("/auth/facescan?register=true")
    assert res.status_code == 200
    assert b"Face Registration" in res.data


def test_register_face_no_session(client):
    res = client.post("/auth/register-face")
    assert res.status_code == 401
    assert b"No user session" in res.data


def test_register_face_no_image(client):
    with client.session_transaction() as sess:
        sess['user_id_for_face'] = 1
    
    res = client.post("/auth/register-face")
    assert res.status_code == 400
    assert b"No face image provided" in res.data


def test_register_face_success(client, mock_face_recognition):
    # Create a test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.jpg', test_image)
    
    with client.session_transaction() as sess:
        sess['user_id_for_face'] = 2  # Use existing test user ID
    
    # Create test data
    data = {
        'face': (img_encoded.tobytes(), 'test.jpg'),
        'label': 'Test Face'
    }
    
    res = client.post("/auth/register-face", 
                     data=data, 
                     content_type='multipart/form-data')
    
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    assert "Face registered successfully" in json_data['message']
    assert json_data['total_faces'] > 0


def test_register_face_no_face_detected(client, mock_face_recognition):
    # Mock no face detected
    mock_face_recognition['locations'].return_value = []
    
    # Create a test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.jpg', test_image)
    
    with client.session_transaction() as sess:
        sess['user_id_for_face'] = 2
    
    data = {
        'face': (img_encoded.tobytes(), 'test.jpg')
    }
    
    res = client.post("/auth/register-face", 
                     data=data, 
                     content_type='multipart/form-data')
    
    assert res.status_code == 400
    assert b"No face detected in image" in res.data


def test_face_status_no_session(client):
    res = client.get("/auth/face-status")
    assert res.status_code == 401
    assert b"No active face recognition session" in res.data


def test_face_status_recognition_success(client):
    with client.session_transaction() as sess:
        sess['user_id_for_face'] = 2
        sess['recognized_face'] = True
    
    res = client.get("/auth/face-status")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True


def test_face_status_recognition_pending(client):
    with client.session_transaction() as sess:
        sess['user_id_for_face'] = 2
    
    res = client.get("/auth/face-status")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is False
