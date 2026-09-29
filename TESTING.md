# Testing the CodeCraftHub API

Copy and paste each command into a terminal, one block at a time, **in order**. Every test shows the command, then the response you should get.

## Before you start

**1. Start the server** in one terminal and leave it running:

```bash
source .venv/bin/activate
python app.py
```

**2. Open a second terminal** and run the tests there.

**3. Start from a clean slate** (so the ids below match). Run this in the project folder:

```bash
rm -f courses.json
```

(The server recreates the file on the next request.)

**How to read the results**

- Every command ends with `-w "\nHTTP status: %{http_code}\n"`, which prints the HTTP status code on the last line.
- `-s` hides curl's progress bar. `-X` picks the method. `-H` sets a header. `-d` is the JSON body.
- `created_at` is the time you ran the command, so yours will differ from the examples.
- JSON keys may appear in a different order, and the server prints them on one line. Both are fine.
- On Windows, use Git Bash or WSL. In `cmd.exe` the single quotes around JSON won't work.

**Troubleshooting**

- `Connection refused`: the server isn't running. Start it (step 1).
- Every request returns `403 Forbidden` or a page that isn't JSON, or the server says the address is in use: on macOS, AirPlay Receiver uses port 5000. Turn it off in *System Settings → General → AirDrop & Handoff → AirPlay Receiver*, or run the server on another port (change `port=5000` at the bottom of `app.py`) and use that port in the commands.

---

# Part 1: Successful operations

## 1.1 Create a course (POST)

Payload: `name`, `description`, `target_date` (YYYY-MM-DD) and `status` are all required.

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Flask Basics", "description": "Learn to build REST APIs with Flask", "target_date": "2026-12-01", "status": "Not Started"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**201 Created**), with `id` set automatically to 1:

```json
{
  "created_at": "2026-09-29T14:30:00",
  "description": "Learn to build REST APIs with Flask",
  "id": 1,
  "name": "Flask Basics",
  "status": "Not Started",
  "target_date": "2026-12-01"
}
HTTP status: 201
```

## 1.2 Create a second course

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Docker Fundamentals", "description": "Containers for developers", "target_date": "2027-01-15", "status": "In Progress"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**201 Created**), with `"id": 2`:

```json
{
  "created_at": "2026-09-29T14:31:00",
  "description": "Containers for developers",
  "id": 2,
  "name": "Docker Fundamentals",
  "status": "In Progress",
  "target_date": "2027-01-15"
}
HTTP status: 201
```

## 1.3 Get all courses (GET)

```bash
curl -s http://127.0.0.1:5000/api/courses -w "\nHTTP status: %{http_code}\n"
```

Expected (**200 OK**): a list with both courses.

```json
[
  {"created_at": "2026-09-29T14:30:00", "description": "Learn to build REST APIs with Flask", "id": 1, "name": "Flask Basics", "status": "Not Started", "target_date": "2026-12-01"},
  {"created_at": "2026-09-29T14:31:00", "description": "Containers for developers", "id": 2, "name": "Docker Fundamentals", "status": "In Progress", "target_date": "2027-01-15"}
]
HTTP status: 200
```

## 1.4 Filter courses by status (GET)

`%20` is a URL-encoded space.

```bash
curl -s "http://127.0.0.1:5000/api/courses?status=In%20Progress" -w "\nHTTP status: %{http_code}\n"
```

Expected (**200 OK**): only Docker Fundamentals.

```json
[
  {"created_at": "2026-09-29T14:31:00", "description": "Containers for developers", "id": 2, "name": "Docker Fundamentals", "status": "In Progress", "target_date": "2027-01-15"}
]
HTTP status: 200
```

## 1.5 Get one course (GET)

```bash
curl -s http://127.0.0.1:5000/api/courses/1 -w "\nHTTP status: %{http_code}\n"
```

Expected (**200 OK**):

```json
{
  "created_at": "2026-09-29T14:30:00",
  "description": "Learn to build REST APIs with Flask",
  "id": 1,
  "name": "Flask Basics",
  "status": "Not Started",
  "target_date": "2026-12-01"
}
HTTP status: 200
```

## 1.6 Update one field (PUT)

Send only what you want to change. Here just the status:

```bash
curl -s -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**200 OK**): same course, new status. `id` and `created_at` did not change.

```json
{
  "created_at": "2026-09-29T14:30:00",
  "description": "Learn to build REST APIs with Flask",
  "id": 1,
  "name": "Flask Basics",
  "status": "In Progress",
  "target_date": "2026-12-01"
}
HTTP status: 200
```

## 1.7 Update several fields (PUT)

```bash
curl -s -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Flask REST APIs", "description": "Build and test a REST API", "target_date": "2026-11-15", "status": "Completed"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**200 OK**):

```json
{
  "created_at": "2026-09-29T14:30:00",
  "description": "Build and test a REST API",
  "id": 1,
  "name": "Flask REST APIs",
  "status": "Completed",
  "target_date": "2026-11-15"
}
HTTP status: 200
```

## 1.8 Delete a course (DELETE)

```bash
curl -s -X DELETE http://127.0.0.1:5000/api/courses/2 -w "\nHTTP status: %{http_code}\n"
```

Expected (**200 OK**): the deleted course is echoed back.

```json
{
  "course": {
    "created_at": "2026-09-29T14:31:00",
    "description": "Containers for developers",
    "id": 2,
    "name": "Docker Fundamentals",
    "status": "In Progress",
    "target_date": "2027-01-15"
  },
  "message": "Course deleted"
}
HTTP status: 200
```

## 1.9 Confirm the delete (GET)

```bash
curl -s http://127.0.0.1:5000/api/courses -w "\nHTTP status: %{http_code}\n"
```

Expected (**200 OK**): only course 1 is left.

```json
[
  {"created_at": "2026-09-29T14:30:00", "description": "Build and test a REST API", "id": 1, "name": "Flask REST APIs", "status": "Completed", "target_date": "2026-11-15"}
]
HTTP status: 200
```

---

# Part 2: Error scenarios

Errors always look like `{"error": "message"}`. Course 1 exists from Part 1. Course 2 was deleted, and 999 never existed.

## 2.1 POST: missing fields

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Only a name"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "Missing required field(s): description, target_date, status"}
HTTP status: 400
```

## 2.2 POST: empty request body

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "Missing required field(s): name, description, target_date, status"}
HTTP status: 400
```

## 2.3 POST: blank name

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "   ", "description": "Blank name", "target_date": "2026-12-01", "status": "Not Started"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "'name' must be a non-empty string"}
HTTP status: 400
```

## 2.4 POST: invalid status

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Bad status", "description": "Status is wrong", "target_date": "2026-12-01", "status": "Done"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "'status' must be one of: Not Started, In Progress, Completed"}
HTTP status: 400
```

## 2.5 POST: wrong date format

Dates must be `YYYY-MM-DD`.

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Bad date", "description": "Date is wrong", "target_date": "01/12/2026", "status": "Not Started"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "'target_date' must be a valid date in YYYY-MM-DD format"}
HTTP status: 400
```

## 2.6 POST: date that doesn't exist

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Impossible date", "description": "Month 13 does not exist", "target_date": "2026-13-45", "status": "Not Started"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "'target_date' must be a valid date in YYYY-MM-DD format"}
HTTP status: 400
```

## 2.7 POST: broken JSON

The body is missing its closing brace.

```bash
curl -s -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Broken JSON"' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "Request body must be a JSON object"}
HTTP status: 400
```

## 2.8 PUT: invalid status

```bash
curl -s -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Finished"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "'status' must be one of: Not Started, In Progress, Completed"}
HTTP status: 400
```

## 2.9 PUT: wrong date format

```bash
curl -s -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"target_date": "next Friday"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**400 Bad Request**):

```json
{"error": "'target_date' must be a valid date in YYYY-MM-DD format"}
HTTP status: 400
```

## 2.10 GET: course not found

```bash
curl -s http://127.0.0.1:5000/api/courses/999 -w "\nHTTP status: %{http_code}\n"
```

Expected (**404 Not Found**):

```json
{"error": "Course not found"}
HTTP status: 404
```

## 2.11 PUT: course not found

```bash
curl -s -X PUT http://127.0.0.1:5000/api/courses/999 \
  -H "Content-Type: application/json" \
  -d '{"status": "Completed"}' \
  -w "\nHTTP status: %{http_code}\n"
```

Expected (**404 Not Found**):

```json
{"error": "Course not found"}
HTTP status: 404
```

## 2.12 DELETE: course not found

Course 2 was already deleted in test 1.8, so deleting it again fails.

```bash
curl -s -X DELETE http://127.0.0.1:5000/api/courses/2 -w "\nHTTP status: %{http_code}\n"
```

Expected (**404 Not Found**):

```json
{"error": "Course not found"}
HTTP status: 404
```

## 2.13 Unknown URL

```bash
curl -s http://127.0.0.1:5000/api/lessons -w "\nHTTP status: %{http_code}\n"
```

Expected (**404 Not Found**):

```json
{"error": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}
HTTP status: 404
```

## 2.14 Id that isn't a number

```bash
curl -s http://127.0.0.1:5000/api/courses/abc -w "\nHTTP status: %{http_code}\n"
```

Expected (**404 Not Found**), same message as 2.13:

```json
{"error": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}
HTTP status: 404
```

## 2.15 Method not allowed

`/api/courses` (without an id) supports only GET and POST, so DELETE is rejected.

```bash
curl -s -X DELETE http://127.0.0.1:5000/api/courses -w "\nHTTP status: %{http_code}\n"
```

Expected (**405 Method Not Allowed**):

```json
{"error": "The method is not allowed for the requested URL."}
HTTP status: 405
```

## 2.16 Corrupted data file (optional)

This checks the file-error handling. It overwrites `courses.json` with invalid JSON, so run it last. Run the first command in the project folder.

```bash
echo "this is not json" > courses.json
```

```bash
curl -s http://127.0.0.1:5000/api/courses -w "\nHTTP status: %{http_code}\n"
```

Expected (**500 Internal Server Error**). The exact wording after the colon may differ:

```json
{"error": "Could not read courses.json: Expecting value: line 1 column 1 (char 0)"}
HTTP status: 500
```

Fix it again by deleting the file (the server recreates it):

```bash
rm -f courses.json
```

---

# Quick reference

| Test | Request | Status |
|------|---------|--------|
| 1.1-1.2 | POST valid course | 201 |
| 1.3-1.5 | GET all / filtered / one / statistics | 200 |
| 1.6-1.7 | PUT valid update | 200 |
| 1.8 | DELETE existing course | 200 |
| 2.1-2.9 | POST/PUT with bad data | 400 |
| 2.10-2.14 | Course or URL not found | 404 |
| 2.15 | Wrong HTTP method | 405 |
| 2.16 | Unreadable data file | 500 |
