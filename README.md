# SAÜ Connect

**English** | [Türkçe](README.tr.md)

A campus platform for Sakarya University (SAÜ) students. Share course notes, ask for help, find teammates for projects, and browse other students' profiles, all in one place.

The interface is in Turkish. It is a single-page web app served by a small Flask backend that stores everything in plain files, so there is no database to set up.

## Features

**Notes**
- Share course notes with a title, description and an optional file attachment (PDFs etc.)
- Like and unlike notes, and download attachments
- A "top notes of the week" highlight section
- Authors can delete their own notes (the attached file is removed too)

**Requests and community**
- Post a request for help or information and let others comment on it
- Browse a directory of students and open their profiles

**Teams**
- Create a team for a project or competition (for example Teknofest) with a description, the skills you need and a target team size
- Other students send join requests with a message; the team owner accepts or rejects them
- Members can leave, owners can kick members or delete the team
- Built-in team chat

**Profiles**
- Register with faculty, department, a short bio and a profile picture
- Public profile pages show a student's notes, requests and teams, plus total notes and likes

**Other**
- Users can report content
- The client polls the server for changes, so lists stay up to date without a manual refresh
- Dark, neumorphic UI built with Tailwind CSS

## Tech stack

- **Backend:** Python 3, [Flask](https://flask.palletsprojects.com/), flask-cors
- **Frontend:** one `index.html` (vanilla JavaScript, Tailwind CSS via CDN, Font Awesome, Google Fonts)
- **Storage:** flat text files and JSON files in `data/`

## Getting started

**Requirements:** Python 3.9 or newer.

```bash
git clone https://github.com/polar-sucks-at-coding/hackathon.git
cd hackathon

pip install flask flask-cors

python networking/server.py
```

Then open <http://localhost:5000> in your browser. Create an account on the sign-up tab and you're in.

The server listens on `0.0.0.0:5000`, so other devices on the same network can reach it at `http://<your-ip>:5000`. The frontend loads Tailwind, Font Awesome and Google Fonts from CDNs, so it needs an internet connection the first time the page loads.

## Project structure

```
.
├── index.html                  # Entire frontend (UI + client-side logic)
├── logo.jpeg
├── user_files/
│   ├── user.py                 # User model (username + password)
│   └── user_profile.py         # Profile model (faculty, department, bio, picture, note IDs)
├── notes/
│   └── note.py                 # Note model
├── networking/
│   ├── server.py               # Flask server and all API handlers
│   └── server_interaction.py   # Older Python socket client (see notes below)
└── data/                       # Created and updated at runtime
    ├── accounts.txt            # username|password
    ├── user_profiles.txt       # profile info and note IDs per user
    ├── notes.txt               # one note per line
    ├── likes.txt               # username|note_id pairs
    ├── next_id.txt             # next note ID
    ├── requests.json           # help requests and comments
    ├── teams.json              # teams, join requests, chat messages
    ├── reports.json            # user reports
    └── uploads/                # uploaded note attachments
```

## API

The server serves `index.html` at `/` and exposes a single endpoint, `POST /api/command`. The body is JSON with a `command` field plus that command's parameters, and every response has a `status` of `success` or `error`.

```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "LOGIN", "username": "ayse", "password": "secret"}'
```

| Area | Commands |
| --- | --- |
| Accounts | `REGISTER`, `LOGIN`, `LOGOUT`, `UPDATE_PROFILE`, `GET_ALL_USERS`, `GET_USER_PROFILE` |
| Notes | `CREATE_NOTE`, `GET_NOTE`, `GET_ALL_NOTES`, `DELETE_NOTE`, `LIKE_NOTE`, `DOWNLOAD_FILE` |
| Requests | `CREATE_REQUEST`, `GET_ALL_REQUESTS`, `DELETE_REQUEST`, `ADD_COMMENT` |
| Teams | `CREATE_TEAM`, `GET_ALL_TEAMS`, `JOIN_TEAM`, `ACCEPT_JOIN_REQUEST`, `REJECT_JOIN_REQUEST`, `LEAVE_TEAM`, `KICK_MEMBER`, `DELETE_TEAM`, `ADD_TEAM_MESSAGE` |
| Moderation | `CREATE_REPORT` |
| Sync | `CHECK_UPDATES` (returns the timestamp of the last data change; the client polls it) |

File uploads and downloads travel as base64 inside the JSON payload.

## Known limitations

This started as a hackathon project and is not production-ready.

- **Passwords are stored in plain text** in `data/accounts.txt`, and there are no sessions or tokens. The API trusts the `username` sent with each request.
- **Storage is flat files** written on every change. Fine for a demo, not for many concurrent users.
- Values are stored pipe-delimited (`|`), so a pipe character in a title or note body will corrupt that line.
- `data/` currently contains sample data and uploads. Clear it out before a real deployment.
- `networking/server_interaction.py` is a leftover socket-based client that no longer matches the HTTP server and isn't used by the web app.

## Ideas for next steps

- Hash passwords and add real authentication (sessions or JWT)
- Move storage to SQLite or PostgreSQL
- Add a `requirements.txt` and a `.gitignore` for `__pycache__/` and runtime data
- Add search and filtering for notes by faculty, department or course

## License

No license file is included yet. Add one if you want others to reuse the code.

## Developer Team

- **Melih Ekinci**
- **Mehmet Yusuf Yöndem**
