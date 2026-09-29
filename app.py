"""CodeCraftHub - a tiny REST API for tracking courses you want to learn.

Courses are stored in a plain JSON file (courses.json). No database, no auth.

Run with:  python app.py   ->  http://127.0.0.1:5000/api/courses
"""
import json
import os
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# Always put the data file next to this script, no matter where you run it from.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses.json")

# The only statuses a course is allowed to have.
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]

# Fields the client must send when creating a course.
REQUIRED_FIELDS = ["name", "description", "target_date", "status"]


# ---------------------------------------------------------------------------
# Storage helpers: reading and writing the JSON file
# ---------------------------------------------------------------------------
class StorageError(Exception):
    """Raised when courses.json can't be read or written."""


def init_data_file():
    """Create courses.json (containing an empty list) if it doesn't exist yet."""
    if not os.path.exists(DATA_FILE):
        save_courses([])


def load_courses():
    """Read every course from the file and return them as a Python list."""
    init_data_file()  # safe to call every time; also recreates a deleted file
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except (OSError, json.JSONDecodeError) as e:
        raise StorageError("Could not read %s: %s" % (os.path.basename(DATA_FILE), e))


def save_courses(courses):
    """Write the whole list of courses back to the file."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(courses, f, indent=2)
    except OSError as e:
        raise StorageError("Could not write %s: %s" % (os.path.basename(DATA_FILE), e))


def next_id(courses):
    """Highest existing id + 1, so ids start at 1 and are never reused."""
    return max((c["id"] for c in courses), default=0) + 1


def find_course(courses, course_id):
    """Return the course with this id, or None if there isn't one."""
    return next((c for c in courses if c["id"] == course_id), None)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_fields(data, partial=False):
    """Check the data sent by the client.

    Returns an error message (str), or None if everything is fine.
    partial=True is used by PUT: only the fields that were sent get checked.
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    # On create, every required field must be present.
    if not partial:
        missing = [k for k in REQUIRED_FIELDS if k not in data]
        if missing:
            return "Missing required field(s): " + ", ".join(missing)

    # Text fields can't be empty.
    for key in ("name", "description"):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            return "'%s' must be a non-empty string" % key

    # Dates must look like 2026-12-31 (and be a real calendar date).
    if "target_date" in data:
        try:
            datetime.strptime(str(data["target_date"]), "%Y-%m-%d")
        except ValueError:
            return "'target_date' must be a valid date in YYYY-MM-DD format"

    # Status must be one of the three allowed values.
    if "status" in data and data["status"] not in VALID_STATUSES:
        return "'status' must be one of: " + ", ".join(VALID_STATUSES)

    return None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def dashboard():
    """Serve the web dashboard (dashboard.html) so it can call the API from the same address."""
    return send_from_directory(os.path.dirname(DATA_FILE), "dashboard.html")


@app.route("/api/courses", methods=["POST"])
def create_course():
    """Add a new course."""
    # silent=True -> returns None instead of raising if the body isn't valid JSON
    data = request.get_json(silent=True)
    error = validate_fields(data)
    if error:
        return jsonify({"error": error}), 400

    courses = load_courses()
    course = {
        "id": next_id(courses),
        "name": data["name"].strip(),
        "description": data["description"].strip(),
        "target_date": data["target_date"],
        "status": data["status"],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    courses.append(course)
    save_courses(courses)
    return jsonify(course), 201  # 201 = Created


@app.route("/api/courses", methods=["GET"])
def list_courses():
    """Get all courses. Optional filter: /api/courses?status=In Progress"""
    courses = load_courses()
    status = request.args.get("status")
    if status:
        courses = [c for c in courses if c["status"] == status]
    return jsonify(courses), 200


@app.route("/api/courses/stats", methods=["GET"])
def course_stats():
    """Get statistics: the total number of courses and how many have each status."""
    courses = load_courses()

    # Start every status at 0 so the response always lists all three,
    # even when no course has that status yet.
    by_status = {status: 0 for status in VALID_STATUSES}
    for course in courses:
        by_status[course["status"]] += 1

    return jsonify({"total": len(courses), "by_status": by_status}), 200


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """Get one course by its id."""
    course = find_course(load_courses(), course_id)
    if course is None:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(course), 200


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """Update a course. Send only the fields you want to change."""
    data = request.get_json(silent=True)
    error = validate_fields(data, partial=True)
    if error:
        return jsonify({"error": error}), 400

    courses = load_courses()
    course = find_course(courses, course_id)
    if course is None:
        return jsonify({"error": "Course not found"}), 404

    # id and created_at are never changed by the client.
    for key in ("name", "description", "target_date", "status"):
        if key in data:
            course[key] = data[key].strip() if key in ("name", "description") else data[key]
    save_courses(courses)
    return jsonify(course), 200


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course by its id."""
    courses = load_courses()
    course = find_course(courses, course_id)
    if course is None:
        return jsonify({"error": "Course not found"}), 404
    courses.remove(course)
    save_courses(courses)
    return jsonify({"message": "Course deleted", "course": course}), 200


# ---------------------------------------------------------------------------
# CORS: let web pages from other addresses (origins) call this API
# ---------------------------------------------------------------------------
@app.after_request
def add_cors_headers(response):
    """Add the headers that tell the browser cross-origin requests are allowed.

    "*" means any website may call the API. That is fine for a local learning
    project with no login; for a real app, list only the origins you trust.
    Browsers also send a "preflight" OPTIONS request before PUT/DELETE/JSON
    requests; Flask answers it automatically and these headers approve it.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ---------------------------------------------------------------------------
# Error handlers: make every error come back as JSON like {"error": "..."}
# ---------------------------------------------------------------------------
@app.errorhandler(StorageError)
def handle_storage_error(e):
    """File read/write problems (missing permissions, corrupted JSON, ...)."""
    return jsonify({"error": str(e)}), 500


@app.errorhandler(HTTPException)
def handle_http_error(e):
    """Unknown URL (404), wrong method (405), etc. -> JSON instead of HTML."""
    return jsonify({"error": e.description}), e.code


# ---------------------------------------------------------------------------
# Start the server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_data_file()  # create courses.json on startup if it's missing
    app.run(debug=True, port=5000)
