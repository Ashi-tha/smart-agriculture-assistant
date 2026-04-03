"""Login, registration, and logout."""
import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from utils.db import create_user, get_user_by_username, get_user_by_id

auth_bp = Blueprint("auth", __name__)

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def _validate_username(username: str) -> bool:
    return bool(username and USERNAME_RE.match(username))


def _validate_password(password: str) -> bool:
    return bool(password and len(password) >= 8)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("index"))
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session.permanent = True
            nxt = (request.form.get("next") or request.args.get("next") or "").strip()
            if nxt.startswith("/") and not nxt.startswith("//"):
                return redirect(nxt)
            return redirect(url_for("index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("index"))
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""

        if not _validate_username(username):
            flash("Username must be 3–32 characters (letters, numbers, underscore only).", "error")
        elif not _validate_password(password):
            flash("Password must be at least 8 characters.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif get_user_by_username(username):
            flash("That username is already taken.", "error")
        else:
            create_user(username, password)
            flash("Account created. You can sign in now.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
