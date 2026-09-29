# CodeCraftHub

A small personal learning tracker: a REST API where developers keep a list of the courses they want to learn, with a target date and a status for each.

Final project of IBM's course on AI assisted Software Engineering.

## Table of contents

1. [Project overview](#1-project-overview)
2. [Features](#2-features)
3. [Installation](#3-installation)
4. [Running the application](#4-running-the-application)
5. [API documentation](#5-api-documentation)
6. [Testing](#6-testing)
7. [Troubleshooting](#7-troubleshooting)
8. [Project structure](#8-project-structure)

---

## 1. Project overview

CodeCraftHub is built to teach **REST API basics**. It is deliberately small:

- **Python + Flask**: Flask is a lightweight web framework. A few lines of Python turn a function into a web address.
- **A JSON file instead of a database**: courses are saved in a plain text file, `courses.json`, that you can open and read.
- **No login**: no accounts, passwords or users to manage, so you can focus on the API itself.

### What is a REST API?

An API lets programs talk to each other. A **REST API** does this over HTTP, the same protocol your browser uses. You send a **request** to a URL and get a **response** back, usually as JSON.

Two things make up a request:

| Part | Meaning | Example |
|------|---------|---------|
| **URL** | *What* you are working with | `/api/courses/1` (course number 1) |
| **Method** | *What you want to do* with it | `GET` = read, `POST` = create, `PUT` = update, `DELETE` = remove |

These four actions (create, read, update, delete) are called **CRUD**. This project implements all of them for one kind of thing: a course.

Every response also has a **status code**, a number that says how it went:

| Code | Meaning |
|------|---------|
| `200` | OK, it worked |
| `201` | Created, a new course was added |
| `400` | Bad request, you sent something invalid |
| `404` | Not found, no such course or URL |
| `405` | Method not allowed |
| `500` | Server error, something is wrong on the server side (for example a damaged data file) |

### What a course looks like

```json
{
  "id": 1,
  "name": "Flask Basics",
  "description": "Learn to build REST APIs with Flask",
  "target_date": "2026-12-01",
  "status": "In Progress",
  "created_at": "2026-09-29T14:30:00"
}
```

| Field | Type | Rules |
|-------|------|-------|
| `id` | number | Set automatically, starting at 1. Never reused, even after a delete. |
| `name` | text | Required. Can't be blank. |
| `description` | text | Required. Can't be blank. |
| `target_date` | text | Required. Format `YYYY-MM-DD`, and must be a real date. |
| `status` | text | Required. Exactly one of `Not Started`, `In Progress`, `Completed`. |
| `created_at` | text | Set automatically when the course is created. Can't be changed. |

## 2. Features

- Full CRUD for courses: create, list, get one, update, delete
- Filter the course list by status (`?status=In Progress`)
- Statistics endpoint: total courses and how many are in each status
- CORS enabled, so web pages hosted elsewhere can call the API
- Automatic `id` and `created_at` for every course
- Input validation with clear error messages (missing fields, bad status, bad date)
- Every error, including unknown URLs and wrong methods, comes back as JSON: `{"error": "..."}`
- `courses.json` is created automatically if it doesn't exist
- Clear error if the data file can't be read or written
- Heavily commented code aimed at beginners
- A copy-and-paste test guide with expected results

## 3. Installation

**You need:** Python 3.8 or newer, and `curl` for trying the API (it comes with macOS and Linux and with recent Windows).

Check your Python version:

```bash
python3 --version
```

> On Windows, use `python` instead of `python3` in all commands.

**Step 1. Get the project** and go into its folder:

```bash
git clone <repository-url>
cd IBM-GenAI-CodeCraftHub
```

(If you already have the folder, just `cd` into it.)

**Step 2. Create a virtual environment.** This is a private box for this project's libraries, so they don't mix with other projects.

```bash
python3 -m venv .venv
```

**Step 3. Activate it.**

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Windows (Command Prompt):

```bat
.venv\Scripts\activate.bat
```

Your prompt now starts with `(.venv)`. You need to activate it again each time you open a new terminal.

**Step 4. Install the dependencies** (only Flask):

```bash
pip install -r requirements.txt
```

## 4. Running the application

With the virtual environment active, start the server:

```bash
python app.py
```

You should see something like:

```
 * Running on http://127.0.0.1:5000
```

The API is now running at **http://127.0.0.1:5000**. Leave this terminal open, since the server runs as long as it does. Stop it with `Ctrl+C`.

On first start, `courses.json` is created next to `app.py` containing an empty list (`[]`).

**Check that it works.** Open a **second** terminal and run:

```bash
curl http://127.0.0.1:5000/api/courses
```

You should get `[]`, an empty list of courses. You can also open that address in your browser.

The server runs in debug mode, so it restarts by itself when you edit `app.py`.

## 5. API documentation

Base URL: `http://127.0.0.1:5000`

| Method | URL | What it does | Success | Errors |
|--------|-----|--------------|---------|--------|
| POST | `/api/courses` | Add a new course | 201 | 400 |
| GET | `/api/courses` | Get all courses (optional `?status=...`) | 200 | |
| GET | `/api/courses/stats` | Get statistics: total and count per status | 200 | |
| GET | `/api/courses/<id>` | Get one course | 200 | 404 |
| PUT | `/api/courses/<id>` | Update a course | 200 | 400, 404 |
| DELETE | `/api/courses/<id>` | Delete a course | 200 | 404 |

In the examples, `-H "Content-Type: application/json"` tells the server you are sending JSON, and `-d` is the JSON you send. The `created_at` values will be your current time.

### Create a course: `POST /api/courses`

All four fields are required.

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Flask Basics", "description": "Learn to build REST APIs with Flask", "target_date": "2026-12-01", "status": "Not Started"}'
```

Response (`201 Created`):

```json
{
  "created_at": "2026-09-29T14:30:00",
  "description": "Learn to build REST APIs with Flask",
  "id": 1,
  "name": "Flask Basics",
  "status": "Not Started",
  "target_date": "2026-12-01"
}
```

### Get all courses: `GET /api/courses`

```bash
curl http://127.0.0.1:5000/api/courses
```

Response (`200 OK`): a list of courses (empty if there are none).

```json
[
  {
    "created_at": "2026-09-29T14:30:00",
    "description": "Learn to build REST APIs with Flask",
    "id": 1,
    "name": "Flask Basics",
    "status": "Not Started",
    "target_date": "2026-12-01"
  }
]
```

To see only courses with a certain status (`%20` stands for a space):

```bash
curl "http://127.0.0.1:5000/api/courses?status=In%20Progress"
```

### Get statistics: `GET /api/courses/stats`

Returns the total number of courses and how many have each status. All three statuses are always listed, with `0` when none match.

```bash
curl http://127.0.0.1:5000/api/courses/stats
```

Response (`200 OK`):

```json
{
  "by_status": {
    "Completed": 1,
    "In Progress": 2,
    "Not Started": 1
  },
  "total": 4
}
```

### Get one course: `GET /api/courses/<id>`

```bash
curl http://127.0.0.1:5000/api/courses/1
```

Response (`200 OK`): the course object, as shown above. If the id doesn't exist you get `404`:

```json
{"error": "Course not found"}
```

### Update a course: `PUT /api/courses/<id>`

Send **only the fields you want to change**. `id` and `created_at` can't be changed.

```bash
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress"}'
```

Response (`200 OK`): the whole updated course.

```json
{
  "created_at": "2026-09-29T14:30:00",
  "description": "Learn to build REST APIs with Flask",
  "id": 1,
  "name": "Flask Basics",
  "status": "In Progress",
  "target_date": "2026-12-01"
}
```

### Delete a course: `DELETE /api/courses/<id>`

```bash
curl -X DELETE http://127.0.0.1:5000/api/courses/1
```

Response (`200 OK`): confirmation plus the deleted course.

```json
{
  "course": {
    "created_at": "2026-09-29T14:30:00",
    "description": "Learn to build REST APIs with Flask",
    "id": 1,
    "name": "Flask Basics",
    "status": "In Progress",
    "target_date": "2026-12-01"
  },
  "message": "Course deleted"
}
```

### Error responses

Every error has the same shape: `{"error": "a message explaining what went wrong"}`.

| Situation | Status | Example message |
|-----------|--------|-----------------|
| Required field missing | 400 | `Missing required field(s): description, target_date, status` |
| Blank name or description | 400 | `'name' must be a non-empty string` |
| Invalid status | 400 | `'status' must be one of: Not Started, In Progress, Completed` |
| Bad or impossible date | 400 | `'target_date' must be a valid date in YYYY-MM-DD format` |
| Body isn't valid JSON | 400 | `Request body must be a JSON object` |
| Course id doesn't exist | 404 | `Course not found` |
| URL doesn't exist | 404 | `The requested URL was not found on the server. ...` |
| Wrong method for a URL | 405 | `The method is not allowed for the requested URL.` |
| Data file unreadable or unwritable | 500 | `Could not read courses.json: ...` |

## 6. Testing

[**TESTING.md**](TESTING.md) is a step-by-step guide with 26 copy-and-paste `curl` tests, each with the exact response you should see:

- **Part 1:** successful operations (create, list, filter, get, update, delete, statistics)
- **Part 2:** error cases (missing fields, invalid data, course not found, wrong method, damaged data file)

The short version:

1. Start the server in one terminal (`python app.py`).
2. In a second terminal, in the project folder, reset the data: `rm -f courses.json`
3. Open [TESTING.md](TESTING.md) and paste the commands one block at a time, **in order**.

You can also explore the API with a graphical tool such as [Postman](https://www.postman.com/) or the VS Code "Thunder Client" extension, using the same URLs and JSON bodies.

## 7. Troubleshooting

**`python3: command not found` / `python: command not found`**
Python isn't installed or isn't on your PATH. Install it from [python.org](https://www.python.org/downloads/). On Windows, try `python` or `py` instead of `python3`.

**`ModuleNotFoundError: No module named 'flask'`**
Flask isn't installed in the Python you are running. Make sure the virtual environment is active (your prompt starts with `(.venv)`), then run `pip install -r requirements.txt`.

**`curl: (7) Failed to connect` / `Connection refused`**
The server isn't running. Start it with `python app.py` in another terminal and leave it open.

**`Address already in use`, or every request returns `403 Forbidden`**
Something else is using port 5000. On macOS this is usually **AirPlay Receiver**: turn it off in *System Settings → General → AirDrop & Handoff → AirPlay Receiver*. Or change the port: at the bottom of `app.py`, edit `app.run(debug=True, port=5000)`, for example to `port=5001`, and use that port in your URLs.

**`400` with `Request body must be a JSON object`**
Your JSON is broken or the header is missing. Check that every `"` and `{ }` is matched and that you included `-H "Content-Type: application/json"`. Keep the JSON in single quotes: `-d '{...}'`.

**JSON commands fail on Windows Command Prompt**
`cmd.exe` doesn't handle single quotes or `\` line breaks the way the examples do. Use Git Bash or WSL, or put the whole command on one line and escape the inner quotes (`\"`).

**`404` when I use a course id**
The course doesn't exist (maybe you deleted it, or reset `courses.json`). Run `curl http://127.0.0.1:5000/api/courses` to see which ids exist. Ids are never reused, so the next course gets a new number.

**`500` with `Could not read courses.json`**
The data file has been damaged, for example by editing it by hand and leaving a typo. Fix the JSON, or delete `courses.json`. The server recreates it, empty. Deleting it also deletes your saved courses.

**`500` with `Could not write courses.json`**
The server can't write in the project folder. Check that the folder is writable and the disk isn't full or read-only.

**My changes to `app.py` don't show up**
Debug mode reloads automatically on save. If it doesn't, stop the server (`Ctrl+C`) and start it again.

## 8. Project structure

```
IBM-GenAI-CodeCraftHub/
├── app.py            # The whole API: storage helpers, validation, endpoints
├── courses.json      # Your data (created automatically; safe to delete to start over)
├── requirements.txt  # Python libraries to install (just Flask)
├── README.md         # This file
├── TESTING.md        # Copy-and-paste curl tests
└── .venv/            # Your virtual environment (created in step 2, not part of the code)
```

### Inside `app.py`

The file is organized top to bottom in five sections:

| Section | What it does |
|---------|--------------|
| **Setup** | Creates the Flask app, and defines where `courses.json` lives and which statuses are allowed. |
| **Storage helpers** | `load_courses()` reads the file into a list. `save_courses()` writes the list back. `next_id()` picks the next id. `find_course()` looks one up. |
| **Validation** | `validate_fields()` checks the data a client sends and returns a helpful message if something is wrong. |
| **Endpoints** | One function per API action. `@app.route(...)` above each function connects it to a URL and a method. |
| **Error handlers** | Turn every error (missing pages, wrong methods, file problems) into a JSON response. |

### How a request flows through the code

For `POST /api/courses`, the steps are:

1. Flask matches the URL and method to `create_course()`.
2. The JSON body is read and checked. If invalid, respond `400` and stop.
3. `load_courses()` reads the current list from `courses.json`.
4. A new course is built with the next `id` and the current time, then added to the list.
5. `save_courses()` writes the list back to the file.
6. The new course is returned with status `201`.

Every action follows the same **load → change → save** pattern. Reads (`GET`) only load.

### Why a JSON file, and its limits

A JSON file is easy to understand and inspect, which makes it good for learning. It is not meant for real applications: it isn't safe when many requests write at once, and it gets slow with lots of data. A real project would use a database. The endpoints wouldn't need to change, only the storage helpers.

## Next steps

Ideas for extending the project once you're comfortable:

- Add a `PATCH` endpoint, or make `PUT` require all fields (in REST, `PUT` traditionally replaces the whole resource)
- Sort or search courses (`?sort=target_date`, `?q=flask`)
- Add automated tests with `pytest` and Flask's test client
- Replace the JSON file with SQLite
