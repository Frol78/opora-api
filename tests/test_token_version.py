from app.main import app  # noqa: F401  импорт, чтобы приложение точно загрузилось


EMAIL = "a@a.ru"
OLD_PASSWORD = "secret123"
NEW_PASSWORD = "newsecret456"


def login(client, password=OLD_PASSWORD):
    response = client.post(
        "/auth/login",
        data={"username": EMAIL, "password": password},
    )
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_смена_пароля_проходит_с_действующим_токеном(client):
    client.post("/auth/register", json={"email": EMAIL, "password": OLD_PASSWORD})
    token = login(client)

    response = client.post(
        "/auth/change-password",
        json={"old_password": OLD_PASSWORD, "new_password": NEW_PASSWORD},
        headers=auth(token),
    )

    assert response.status_code == 200


def test_старый_токен_перестаёт_работать_после_смены_пароля(client):
    client.post("/auth/register", json={"email": EMAIL, "password": OLD_PASSWORD})
    old_token = login(client)

    client.post(
        "/auth/change-password",
        json={"old_password": OLD_PASSWORD, "new_password": NEW_PASSWORD},
        headers=auth(old_token),
    )

    # Тем же старым токеном пробуем ещё раз: token_version уже не совпадает
    response = client.post(
        "/auth/change-password",
        json={"old_password": NEW_PASSWORD, "new_password": "third789"},
        headers=auth(old_token),
    )

    assert response.status_code == 401


def test_новый_токен_работает_после_смены_пароля(client):
    client.post("/auth/register", json={"email": EMAIL, "password": OLD_PASSWORD})
    client.post(
        "/auth/change-password",
        json={"old_password": OLD_PASSWORD, "new_password": NEW_PASSWORD},
        headers=auth(login(client)),
    )

    # Входим уже с новым паролем и получаем свежий токен
    new_token = login(client, password=NEW_PASSWORD)

    response = client.post(
        "/auth/change-password",
        json={"old_password": NEW_PASSWORD, "new_password": "third789"},
        headers=auth(new_token),
    )

    assert response.status_code == 200
