import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_taskmanager.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from main import app
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def auth_token(client):
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    })
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass123",
    })
    return response.json()["access_token"]


# ── Auth Tests ──────────────────────────────────────────────────────────────

def test_register(client):
    res = client.post("/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
    })
    assert res.status_code == 201
    assert res.json()["username"] == "newuser"


def test_register_duplicate_username(client):
    client.post("/register", json={"username": "dupeuser", "email": "a@b.com", "password": "pass"})
    res = client.post("/register", json={"username": "dupeuser", "email": "c@d.com", "password": "pass"})
    assert res.status_code == 400


def test_login(client, auth_token):
    assert auth_token is not None


def test_login_wrong_password(client):
    client.post("/register", json={"username": "wrongpassuser", "email": "wp@wp.com", "password": "correct"})
    res = client.post("/login", data={"username": "wrongpassuser", "password": "wrong"})
    assert res.status_code == 401


# ── Task Tests ───────────────────────────────────────────────────────────────

def test_create_task(client, auth_token):
    res = client.post(
        "/tasks",
        json={"title": "Test Task", "description": "A test task"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert res.status_code == 201
    assert res.json()["title"] == "Test Task"
    assert res.json()["completed"] is False


def test_get_tasks(client, auth_token):
    res = client.get("/tasks", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "tasks" in data
    assert "total" in data


def test_get_task_by_id(client, auth_token):
    create_res = client.post(
        "/tasks",
        json={"title": "Specific Task"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    task_id = create_res.json()["id"]
    res = client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert res.json()["id"] == task_id


def test_update_task(client, auth_token):
    create_res = client.post(
        "/tasks",
        json={"title": "Update Me"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    task_id = create_res.json()["id"]
    res = client.put(
        f"/tasks/{task_id}",
        json={"completed": True},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert res.status_code == 200
    assert res.json()["completed"] is True


def test_delete_task(client, auth_token):
    create_res = client.post(
        "/tasks",
        json={"title": "Delete Me"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    task_id = create_res.json()["id"]
    res = client.delete(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 204


def test_get_nonexistent_task(client, auth_token):
    res = client.get("/tasks/99999", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 404


def test_filter_completed_tasks(client, auth_token):
    res = client.get("/tasks?completed=true", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    for task in res.json()["tasks"]:
        assert task["completed"] is True


def test_unauthorized_access(client):
    res = client.get("/tasks")
    assert res.status_code == 401
