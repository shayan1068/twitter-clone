from functools import wraps
from flask import g, flash, redirect, url_for,abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect(url_for('homepage'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or not g.user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function