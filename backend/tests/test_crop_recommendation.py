"""Tests for ML Crop Recommendation service and endpoints."""


def test_model_info_endpoint(client):
    response = client.get("/api/v1/crop-recommendation/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "SVM" in data["modelName"]
    assert data["testAccuracy"] > 90.0
    assert len(data["classes"]) == 22
    assert "rice" in data["classes"]
    assert "apple" in data["classes"]


def test_presets_endpoint(client):
    response = client.get("/api/v1/crop-recommendation/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 3
    assert any(p["id"] == "paddy-monsoon" for p in presets)


def test_predict_paddy(client):
    payload = {
        "nitrogen": 90.0,
        "phosphorus": 42.0,
        "potassium": 43.0,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9,
    }
    response = client.post("/api/v1/crop-recommendation/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommendedCrop"] == "rice"
    assert data["confidence"] > 50.0
    assert "agronomicGuide" in data
    assert data["agronomicGuide"]["season"] != ""
    assert len(data["alternatives"]) <= 3


def test_predict_apple(client):
    payload = {
        "nitrogen": 24.0,
        "phosphorus": 130.0,
        "potassium": 200.0,
        "temperature": 22.5,
        "humidity": 92.0,
        "ph": 6.2,
        "rainfall": 110.0,
    }
    response = client.post("/api/v1/crop-recommendation/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommendedCrop"] == "apple"


def test_predict_validation_error(client):
    # Invalid negative nitrogen
    payload = {
        "nitrogen": -10.0,
        "phosphorus": 42.0,
        "potassium": 43.0,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9,
    }
    response = client.post("/api/v1/crop-recommendation/predict", json=payload)
    assert response.status_code == 422
