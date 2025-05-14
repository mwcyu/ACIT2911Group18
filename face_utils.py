import face_recognition
import cv2
import numpy as np
import os
import json
from flask import session

def load_known_faces():
    known_face_encodings = []
    known_face_names = []
    known_customer_ids = []
    
    # Load face encodings from database
    from db import db
    from models import Customer
    
    # Get all customers with face encodings
    stmt = db.select(Customer).where(Customer.face_encodings.is_not(None))
    customers = db.session.execute(stmt).scalars()
    
    for customer in customers:
        if customer.face_encodings:
            for i, encoding in enumerate(customer.face_encodings):
                known_face_encodings.append(np.array(encoding))
                label = customer.face_labels[i] if customer.face_labels and i < len(customer.face_labels) else None
                known_face_names.append(f"{customer.name} ({label})" if label else customer.name)
                known_customer_ids.append(customer.id)
    
    return known_face_encodings, known_face_names, known_customer_ids

def gen_face_recognition_stream():
    video_capture = cv2.VideoCapture(0)
    
    known_face_encodings, known_face_names, known_customer_ids = load_known_faces()
    process_this_frame = True

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_names = []
        face_confidences = []  # Store confidence scores
        face_locations = []

        if process_this_frame:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])            # Find faces in the frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding in face_encodings:
                name = "Unknown"
                confidence = 0.0
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    best_distance = face_distances[best_match_index]
                    confidence = 1 - best_distance
                    name = known_face_names[best_match_index]
                    
                    # Require higher confidence for direct login vs verification
                    min_confidence = 0.7 if "direct_face_login" in session else 0.6
                    
                    if confidence >= min_confidence:
                          # Check if we're in a face recognition session
                        if "user_id_for_face" in session:
                            customer_id = known_customer_ids[best_match_index]
                            if customer_id == session["user_id_for_face"] and confidence > 0.6:
                                session["recognized_face"] = True
                                session["confidence"] = float(confidence)
                        # Handle direct face login
                        elif "direct_face_login" in session and confidence > 0.7:  # Higher confidence for direct login
                            customer_id = known_customer_ids[best_match_index]
                            session["recognized_face"] = True
                            session["user_id_for_face"] = customer_id
                            session["confidence"] = float(confidence)

                face_names.append(name)
                face_confidences.append(confidence)

        process_this_frame = not process_this_frame

        # Draw results
        for (top, right, bottom, left), name, confidence in zip(face_locations, face_names, face_confidences):
            # Scale back up face locations
            top *= 4; right *= 4; bottom *= 4; left *= 4
            
            # Draw box around face
            color = (0, 255, 0) if confidence > 0.6 else (0, 0, 255)  # Green if confident, red if not
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label with name and confidence
            label = f"{name} ({confidence:.0%})"
            y = bottom - 10 if bottom - 10 > 10 else top + 10
            cv2.putText(frame, label, (left + 6, y), cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 1)

        # Encode and stream
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
