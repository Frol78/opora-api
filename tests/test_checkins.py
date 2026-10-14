from app.main import app  # noqa: F401


USER_A = "alice@a.ru"
USER_B = "bob@b.ru"
PASSWORD = "secret123"

CHECKIN = {"mood": 7, "craving": 3, "note": "Тестовая запись"}


def register_and_login(client, email):
    client.post("/auth/register", json={"email": email, "password": PASSWORD})
    response = client.post(
        "/auth/login",
        data={"username": email, "password": PASSWORD},
    )
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_без_токена_нельзя_создать_и_читать(client):
    assert client.post("/checkins/", json=CHECKIN).status_code == 401
    assert client.get("/checkins/").status_code == 401


def test_свой_чекин_создаётся_и_читается(client):
    token = register_and_login(client, USER_A)

    created = client.post("/checkins/", json=CHECKIN, headers=auth(token))
    assert created.status_code == 201
    checkin_id = created.json()["id"]

    response = client.get(f"/checkins/{checkin_id}", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["note"] == "Тестовая запись"


def test_список_показывает_только_свои_записи(client):
    token_a = register_and_login(client, USER_A)
    token_b = register_and_login(client, USER_B)
    client.post("/checkins/", json=CHECKIN, headers=auth(token_a))
    client.post("/checkins/", json=CHECKIN, headers=auth(token_a))
    client.post("/checkins/", json=CHECKIN, headers=auth(token_b))

    response_a = client.get("/checkins/", headers=auth(token_a))
    response_b = client.get("/checkins/", headers=auth(token_b))
    assert response_a.status_code == 200
    assert len(response_a.json()) == 2
    assert len(response_b.json()) == 1


def test_чужой_чекин_не_виден_и_не_удаляется(client):
    token_a = register_and_login(client, USER_A)
    token_b = register_and_login(client, USER_B)
    checkin_id = client.post(
        "/checkins/", json=CHECKIN, headers=auth(token_a)
    ).json()["id"]

    assert client.get(f"/checkins/{checkin_id}", headers=auth(token_b)).status_code == 404
    assert client.delete(f"/checkins/{checkin_id}", headers=auth(token_b)).status_code == 404

    # У владельца запись осталась
    assert client.get(f"/checkins/{checkin_id}", headers=auth(token_a)).status_code == 200


def test_свой_чекин_удаляется(client):
    token = register_and_login(client, USER_A)
    checkin_id = client.post(
        "/checkins/", json=CHECKIN, headers=auth(token)
    ).json()["id"]

    assert client.delete(f"/checkins/{checkin_id}", headers=auth(token)).status_code == 204
    assert client.get(f"/checkins/{checkin_id}", headers=auth(token)).status_code == 404
