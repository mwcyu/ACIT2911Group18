"""Unit tests for email utilities"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from email_utils import (
    generate_reset_token,
    verify_reset_token,
    send_password_reset_email,
    render_reset_email
)

class TestTokenGeneration:
    def test_generate_reset_token(self, app):
        """Test reset token generation"""
        with app.app_context():
            phone = "+1-604-555-0123"
            token = generate_reset_token(phone)
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0
            
            # Token should be verifiable
            decoded_phone = verify_reset_token(token)
            assert decoded_phone == phone

    def test_verify_expired_token(self, app):
        """Test expired token verification"""
        with app.app_context():
            phone = "+1-604-555-0123"
            token = generate_reset_token(phone)
            # Test with explicit expiration
            assert verify_reset_token(token, max_age=1) is not None  # Should work with 1 second
            import time
            time.sleep(2)  # Wait for token to expire
            assert verify_reset_token(token, max_age=1) is None  # Should fail after expiration

    def test_verify_invalid_token(self, app):
        """Test invalid token verification"""
        with app.app_context():
            # Test completely invalid token
            assert verify_reset_token("invalid-token") is None
            
            # Test malformed but properly formatted token
            s = URLSafeTimedSerializer("wrong-secret-key")
            bad_token = s.dumps("test", salt="password-reset")
            assert verify_reset_token(bad_token) is None

            # Test empty token
            assert verify_reset_token("") is None
            assert verify_reset_token(None) is None

class TestEmailRendering:
    def test_render_reset_email(self):
        """Test password reset email rendering"""
        name = "John Doe"
        reset_url = "http://example.com/reset"
        email_body = render_reset_email(name, reset_url)
        
        # Email should contain key information
        assert name in email_body
        assert reset_url in email_body
        assert "password" in email_body.lower()
        assert "reset" in email_body.lower()

class TestEmailSending:
    @patch('email_utils.url_for')
    def test_send_password_reset_email(self, mock_url_for, app, test_user):
        """Test password reset email sending"""
        mock_url_for.return_value = 'http://test.com/reset'
        mock_mail = MagicMock()
        
        with app.app_context():
            app.extensions = {'mail': mock_mail}
            send_password_reset_email(test_user)
            
            # Verify mail.send was called correctly
            assert mock_mail.send.called
            msg = mock_mail.send.call_args[0][0]
            assert isinstance(msg, Message)
            assert msg.recipients == [test_user.email]
            assert msg.subject == "Reset Your Password"
            assert test_user.name in msg.body
            assert "http://test.com/reset" in msg.body

    @patch('email_utils.url_for')
    def test_send_email_failure(self, mock_url_for, app, test_user):
        """Test handling of email sending failures"""
        mock_url_for.return_value = 'http://test.com/reset'
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("Mail sending failed")
        
        with app.app_context():
            app.extensions = {'mail': mock_mail}
            # Should not raise an exception
            send_password_reset_email(test_user)