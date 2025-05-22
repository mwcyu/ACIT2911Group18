Setup:

```python
python -m venv venv
source venv/bin/activate  # or Scripts\activate on Windows
pip install -r requirements.txt
```

May 2nd

Marco Yu:

1. I moved all the login logout register stuff to the auth.py
2. added API route to toggle admin
3. Added admin column for customer
4. Added admin dashboard to toggle in season projects

5. Redoing the log in system with WTForms and Flask-WTF for added CSRF protection with form.hidden_tag()

## What is CSRF?

CSRF stands for Cross-Site Request Forgery.

It’s a type of web security vulnerability where a malicious website tricks a user into submitting a request to another website where they're already authenticated. If the victim is logged in (e.g. to your Flask app), the malicious request could do something harmful — like submit a form or change account details — without the user's permission.

6. I added forget password, reset password

May 7th

1. Added Testing for cart and auth (login)
2. Added Active Cart (Cusotmer can have multiple pending orders, but only 1 is their active cart)
3. Added Cart Template
4. Add and remove items from cart
5. Change product quantities from cart
6. Generate order under a budget (Routes and templates)
7. Added Dark mode toggle, saved as cookies

Pytest made:

1. add items to cart
2. update cart item quantity
3. remove cart item
4. Generate Cart under budget

Auth test:

1. Correctly hash password in database
2. Accessing Login page
3. Test if you can log in to dashboard with the correct credentials
