from io import BytesIO

from PIL import Image


def test_home_redirects_to_login_without_session(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_home_page_loads_when_logged_in(logged_in_client):
    response = logged_in_client.get("/")
    assert response.status_code == 200


def test_weather_requires_city(logged_in_client):
    response = logged_in_client.get("/api/weather")
    assert response.status_code == 400


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_disease_missing_image_returns_400(logged_in_client):
    response = logged_in_client.post("/api/disease")
    assert response.status_code == 400


def test_disease_returns_503_when_weights_missing(logged_in_client, monkeypatch):
    import routes.disease as disease_mod

    monkeypatch.setattr(disease_mod, "WEIGHTS_PATH", "/__missing_rice_weights__.h5")
    disease_mod._init_done = False
    disease_mod._model = None
    disease_mod._weights_loaded = False

    buf = BytesIO()
    Image.new("RGB", (32, 32), color=(20, 140, 40)).save(buf, format="PNG")
    buf.seek(0)

    response = logged_in_client.post(
        "/api/disease",
        data={"image": (buf, "rice.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 503
    body = response.get_json()
    assert body["success"] is False
    assert "errors" in body


def test_api_requires_auth(client):
    response = client.get("/api/weather")
    assert response.status_code == 401
