import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///todo.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

STATIC_BASE_URL = os.environ.get("STATIC_BASE_URL", "")

db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    done = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(10), default="medium")  # low / medium / high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "done": self.done,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }


@app.context_processor
def inject_static_base():
    return {"static_base": STATIC_BASE_URL}

@app.route("/")
def index():
    filter_by = request.args.get("filter", "all")
    priority = request.args.get("priority", "all")

    query = Todo.query
    if filter_by == "active":
        query = query.filter_by(done=False)
    elif filter_by == "done":
        query = query.filter_by(done=True)

    if priority in ("low", "medium", "high"):
        query = query.filter_by(priority=priority)

    todos = query.order_by(Todo.created_at.desc()).all()

    stats = {
        "total": Todo.query.count(),
        "done": Todo.query.filter_by(done=True).count(),
        "active": Todo.query.filter_by(done=False).count(),
    }

    return render_template(
        "index.html",
        todos=todos,
        stats=stats,
        current_filter=filter_by,
        current_priority=priority,
    )


@app.route("/todo/add", methods=["POST"])
def add_todo():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "medium")

    if not title:
        return redirect(url_for("index"))

    todo = Todo(title=title, description=description or None, priority=priority)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/todo/<int:todo_id>/toggle", methods=["POST"])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.done = not todo.done
    db.session.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/todo/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/todo/<int:todo_id>/edit", methods=["GET", "POST"])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if title:
            todo.title = title
            todo.description = request.form.get("description", "").strip() or None
            todo.priority = request.form.get("priority", "medium")
            db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", todo=todo)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
