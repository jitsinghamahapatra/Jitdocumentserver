import os
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect,
    url_for, send_from_directory, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# ---------------- CONFIG ----------------
app = Flask(__name__)
app.secret_key = "b131f4537789c39e48d03b52bbb5c58f"  # keep this secret

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "docs.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Admin password
ADMIN_PASSWORD = "Jit@2006"

db = SQLAlchemy(app)

# ---------------- DATABASE ----------------
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False, unique=True)
    uploaded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=5, minutes=30)  # IST TIME FIX
    )

    def is_image(self):
        ext = os.path.splitext(self.filename)[1].lower()
        return ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]


# ---------------- HELPER ----------------
def is_admin():
    return session.get("is_admin") is True


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect(url_for("gallery"))


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Logged in as admin.", "success")
            return redirect(url_for("admin_panel"))
        else:
            flash("Wrong password!", "danger")
    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    flash("Logged out.", "info")
    return redirect(url_for("gallery"))


# ADMIN PANEL
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not is_admin():
        return redirect(url_for("login"))

    if request.method == "POST":
        display_name = request.form.get("display_name")
        file = request.files.get("file")

        if not display_name or not file:
            flash("Please provide a name and a file.", "warning")
            return redirect(url_for("admin_panel"))

        filename = secure_filename(file.filename)
        if not filename:
            flash("Invalid file name.", "danger")
            return redirect(url_for("admin_panel"))

        # avoid overwrite
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(datetime.utcnow().timestamp())}{ext}"

        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        doc = Document(display_name=display_name, filename=filename)
        db.session.add(doc)
        db.session.commit()
        flash("File uploaded successfully.", "success")

        return redirect(url_for("admin_panel"))

    docs = Document.query.order_by(Document.uploaded_at.desc()).all()
    return render_template("admin.html", docs=docs)


# EDIT
@app.route("/admin/edit/<int:doc_id>", methods=["POST"])
def edit_doc(doc_id):
    if not is_admin():
        return redirect(url_for("login"))
    doc = Document.query.get_or_404(doc_id)
    new_name = request.form.get("display_name")
    if new_name:
        doc.display_name = new_name
        db.session.commit()
        flash("Name updated.", "success")
    else:
        flash("Name cannot be empty.", "warning")
    return redirect(url_for("admin_panel"))


# DELETE
@app.route("/admin/delete/<int:doc_id>", methods=["POST"])
def delete_doc(doc_id):
    if not is_admin():
        return redirect(url_for("login"))
    doc = Document.query.get_or_404(doc_id)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted.", "info")
    return redirect(url_for("admin_panel"))


# PUBLIC GALLERY
@app.route("/gallery")
def gallery():
    docs = Document.query.order_by(Document.uploaded_at.desc()).all()
    return render_template("gallery.html", docs=docs)


# DOWNLOAD
@app.route("/download/<int:doc_id>")
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return send_from_directory(app.config["UPLOAD_FOLDER"], doc.filename, as_attachment=True)


# SERVE FILES
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
