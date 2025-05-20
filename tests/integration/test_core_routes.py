import pytest
from flask import url_for
from models import Coupon, Season, Order

class TestCoreRoutes:

    def test_dashboard_page(self, logged_in_client):
        """Ensure dashboard page loads for authenticated user."""
        response = logged_in_client.get("/dashboard")
        assert response.status_code == 200
        assert b"Order" in response.data

    def test_home_redirects_to_season(self, logged_in_client, db, test_user):
        """Test home page redirects to seasonal route if active season exists."""
        spring = Season(name="spring", active=True)
        db.session.add(spring)
        db.session.commit()

        response = logged_in_client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/spring" in response.headers["Location"]

    def test_home_renders_without_active_season(self, logged_in_client):
        """Ensure home renders with no active season."""
        response = logged_in_client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert b"Categories" in response.data or b"Home" in response.data

    @pytest.mark.parametrize("season", ["spring", "summer", "fall", "winter"])
    def test_seasonal_pages_render(self, client, test_category, test_product, season, db):
        """Check seasonal routes like /spring, /summer, etc."""
        test_product.season_name = season
        db.session.commit()
        response = client.get(f"/{season}")
        assert response.status_code == 200
        assert season.encode() in response.data or test_product.name.encode() in response.data

    def test_spin_wheel_get(self, logged_in_client, db):
        """Check spin wheel page loads and shows coupon options."""
        c = Coupon(code="SAVE10", discount_amount=10.0, is_percent=False, active=True)
        db.session.add(c)
        db.session.commit()

        response = logged_in_client.get("/spin-wheel")
        assert response.status_code == 200
        assert b"SAVE10" in response.data

    def test_spin_wheel_claim_coupon(self, logged_in_client, test_user, db):
        """Ensure a coupon can be claimed by a user."""
        coupon = Coupon(code="EXTRA5", discount_amount=5.0, is_percent=False, active=True)
        db.session.add(coupon)
        db.session.commit()

        response = logged_in_client.post(
            "/spin-wheel",
            data={"coupon_code": coupon.code},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert coupon in test_user.coupons

    def test_apply_coupon_flash(self, logged_in_client):
        """Test /apply-coupon flashes a message and redirects to cart.generate_cart"""
        response = logged_in_client.post(
            "/apply-coupon",
            data={"coupon_code": "TEST123"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Coupon TEST123 applied!" in response.data
