from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from flask_login import login_user, logout_user, login_required
import face_recognition
import cv2
import numpy as np
import os
import json

from forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from models import Customer
from db import db
from email_utils import send_password_reset_email, verify_reset_token

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        phone = form.phone.data.strip()
        password = form.password.data.strip()
        
        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar_one_or_none()
        
        if customer:
            session["user_id_for_face"] = customer.id
            if customer.face_encodings and len(customer.face_encodings) > 0:
                return redirect(url_for("auth.facescan"))
            else:
                # If no face registered, log in directly
                login_user(customer)
                return redirect(url_for("dashboard_page"))
        else:
            flash("Invalid phone number or password.", "danger")

    return render_template("login.html", form=form)

@auth_bp.route("/facescan", methods=["GET", "POST"])
def facescan():
    # Check if this is for registration or login
    register_mode = request.args.get('register', 'false').lower() == 'true'
    
    # For direct face login, we don't set user_id_for_face
    # The face recognition will match against all registered faces
    if not register_mode and "user_id_for_face" not in session:
        session["direct_face_login"] = True
        
    return render_template("facescan.html", register_mode=register_mode)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        name = form.name.data.strip()
        phone = form.phone.data.strip()
        email = form.email.data.strip()
        password = form.password.data.strip()

        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar_one_or_none()

        if customer:
            return jsonify({"error": "This phone number already has an account"})

        new_customer = Customer(name=name, phone=phone, email=email)
        new_customer.set_password(password)
        db.session.add(new_customer)
        db.session.commit()
        
        login_user(new_customer)
        session["user_id_for_face"] = new_customer.id

        return jsonify({"success": True, "message": "Registration successful!"})

    return render_template("register.html", form=form)

@auth_bp.route("/register-face", methods=["POST"])
def register_face():
    if "user_id_for_face" not in session:
        return jsonify({"error": "No user session"}), 401
    
    if not request.files.get("face"):
        return jsonify({"error": "No face image provided"}), 400

    customer_id = session["user_id_for_face"]
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "User not found"}), 404

    face_image = request.files["face"].read()
    # Convert to numpy array
    nparr = np.frombuffer(face_image, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert BGR to RGB (face_recognition uses RGB)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect face locations
    face_locations = face_recognition.face_locations(rgb_img)
    if not face_locations:
        return jsonify({"error": "No face detected in image"}), 400

    # Get face encoding
    face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
      # Add the new face encoding with an optional label from the form
    label = request.form.get('label', None)
    
    # Initialize face_encodings if None
    if customer.face_encodings is None:
        customer.face_encodings = []
        customer.face_labels = []
    
    # Add the new face encoding and label
    customer.face_encodings.append(face_encoding.tolist())
    customer.face_labels.append(label or f"Face {len(customer.face_encodings)}")
    
    # Commit changes to database
    db.session.commit()
    
    # Get the updated count
    total_faces = len(customer.face_encodings)
    return jsonify({
        "success": True,
        "message": f"Face registered successfully! You now have {total_faces} face{'s' if total_faces != 1 else ''} registered.",
        "total_faces": total_faces
    })

@auth_bp.route("/face-status")
def face_status():
    # Check for direct face login
    is_direct_login = "direct_face_login" in session
    
    # Allow status checks for both direct login and regular face verification
    if not is_direct_login and "user_id_for_face" not in session:
        return jsonify({"error": "No active face recognition session"}), 401
    
    if "recognized_face" in session:
        user_id = session.pop("user_id_for_face", None)
        session.pop("recognized_face", None)
        session.pop("direct_face_login", None)
        confidence = session.pop("confidence", 0)
        
        # Log the user in
        customer = db.session.get(Customer, user_id)
        if customer:
            login_user(customer)
            return jsonify({
                "success": True,
                "confidence": confidence,
                "redirect_url": url_for("dashboard_page")
            })
    
    return jsonify({"success": False})

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        phone = form.phone.data.strip()
        customer = db.session.scalar(db.select(Customer).where(Customer.phone == phone))

        if customer:
            send_password_reset_email(customer)
            flash("A password reset link has been sent to your email.", "info")
            return redirect(url_for("auth.login"))
        else:
            flash("No account found with that phone number.", "warning")

    return render_template("forgot_password.html", form=form)

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    phone = verify_reset_token(token)
    if not phone:
        flash("The reset link is invalid or expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    customer = db.session.scalar(db.select(Customer).where(Customer.phone == phone))
    if not customer:
        flash("Invalid user.", "danger")
        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        customer.set_password(form.password.data.strip())
        db.session.commit()
        flash("Your password has been updated.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)