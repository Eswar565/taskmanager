# TaskFlow – FastAPI Task Manager

A simple Task Manager web application with JWT authentication, built with FastAPI (backend) and plain HTML/JS (frontend).

## Live Demo
> Add your deployed link here after deployment

---

## Features

- **JWT Authentication** – register, login, secure token-based access
- **Full Task CRUD** – create, view, update, delete tasks
- **Ownership** – users only see their own tasks
- **Filtering** – `?completed=true/false` query param
- **Pagination** – `?page=1&page_size=10`
- **Basic Frontend** – register, login, create, view, complete, and delete tasks
- **Swagger UI** – available at `/docs`

---

## Project Structure

```
taskmanager/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── .env.example
│   └── app/
│       ├── core/
│       │   └── security.py      # JWT + bcrypt utils
│       ├── db/
│       │   └── database.py      # SQLAlchemy engine + session
│       ├── models/
│       │   ├── user.py          # User ORM model
│       │   └── task.py          # Task ORM model
│       ├── routers/
│       │   ├── auth.py          # /register, /login
│       │   └── tasks.py         # /tasks CRUD
│       └── schemas/
│           ├── user.py          # Pydantic user schemas
│           └── task.py          # Pydantic task schemas
├── frontend/
│   └── index.html               # Single-page frontend
└── tests/
    └── test_api.py              # Pytest test cases
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | No | Create account |
| POST | `/login` | No | Get JWT token |
| POST | `/tasks` | Yes | Create task |
| GET | `/tasks` | Yes | List tasks (paginated, filterable) |
| GET | `/tasks/{id}` | Yes | Get single task |
| PUT | `/tasks/{id}` | Yes | Update task |
| DELETE | `/tasks/{id}` | Yes | Delete task |
| GET | `/docs` | No | Swagger UI |

**Filter examples:**
```
GET /tasks?completed=true
GET /tasks?completed=false&page=2&page_size=5
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./taskmanager.db
```

> ⚠️ Never commit `.env` to version control.

---

## Run Locally

### Prerequisites
- Python 3.11+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Edit SECRET_KEY before running
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

### Frontend Setup

Open `frontend/index.html` directly in your browser — no build step required.

> Make sure the `API` base URL in `index.html` matches where your backend is running.

---

## Run Tests

```bash
cd backend
pytest tests/ -v
```

---

## Docker

```bash
cd backend
docker build -t taskflow-api .
docker run -p 8000:8000 --env-file .env taskflow-api
```

---

## Deploy to Render

1. Push code to a public GitHub repo
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your repo, set **Root Directory** to `backend`
4. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Add environment variables from `.env.example` in the Render dashboard
6. Deploy

For the frontend, deploy `frontend/index.html` as a **Static Site** on Render or Vercel.  
Update the `API` const in `index.html` to your backend's live URL before deploying frontend.
