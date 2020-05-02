import functools
from flask import session, flash, url_for, redirect, render_template


def login_required(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if session.get("logged_in"):
            return func(*args, **kwargs)
        else:
            return render_template("message_for_user.html", title="Info", message="You must login first.")

    return wrap
