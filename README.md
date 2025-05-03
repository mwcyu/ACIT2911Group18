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
