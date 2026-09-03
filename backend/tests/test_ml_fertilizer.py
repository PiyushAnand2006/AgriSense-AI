"""Tests for ML Fertilizer Prediction service, endpoints, and validation."""


def test_ml_fertilizer_info_endpoint(client):
    response = client.get("/api/v1/fertilizer/ml-info")
    assert response.status_code == 200
    data = response.json()
    assert "XGBoost" in data["modelName"]
    assert data["testAccuracy"] > 90.0
    assert len(data["classes"]) == 7
    assert "Urea" in data["classes"]
    assert "DAP" in data["classes"]
    assert "17-17-17" in data["classes"]
    assert len(data["features"]) == 39
    assert "Kharif" in data["supportedSeasons"]
    assert "Clayey" in data["supportedSoils"]


def test_ml_fertilizer_presets_endpoint(client):
    response = client.get("/api/v1/fertilizer/ml-presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 3
    assert any(p["id"] == "rice-kharif-urea" for p in presets)


def test_predict_fertilizer_rice_kharif(client):
    payload = {
        "crop": "rice",
        "season": "Kharif",
        "soilType": "Clayey",
        "nitrogen": 35.0,
        "phosphorous": 18.0,
        "potassium": 12.0,
        "temperature": 26.0,
        "humidity": 70.0,
        "moisture": 35.0,
    }
    response = client.post("/api/v1/fertilizer/ml-predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["prediction"] in ["Urea", "DAP", "17-17-17", "10-26-26", "14-35-14", "20-20", "28-28"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert 0.0 <= data["confidencePct"] <= 100.0
    assert "profile" in data and data["profile"] is not None
    assert "npkRatio" in data["profile"]
    assert "primaryFunction" in data["profile"]
    assert data["inputSummary"]["crop"] == "rice"
    assert data["inputSummary"]["season"] == "Kharif"
    assert len(data["probabilities"]) == 7
    assert data["disclaimer"] != ""


def test_predict_fertilizer_alias_route(client):
    payload = {
        "crop": "cotton",
        "season": "Kharif",
        "soil_type": "Black",
        "nitrogen": 40.0,
        "phosphorous": 30.0,
        "potassium": 40.0,
        "temperature": 29.0,
        "humidity": 65.0,
        "moisture": 30.0,
    }
    response = client.post("/api/v1/fertilizers/ml-predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["prediction"] != ""


def test_predict_fertilizer_wheat_rabi(client):
    payload = {
        "crop": "wheat",
        "season": "Rabi",
        "soilType": "Loamy",
        "nitrogen": 22.0,
        "phosphorous": 65.0,
        "potassium": 28.0,
        "temperature": 18.0,
        "humidity": 45.0,
        "moisture": 40.0,
    }
    response = client.post("/api/v1/fertilizer/ml-predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_predict_invalid_crop(client):
    payload = {
        "crop": "dragonfruit_unsupported",
        "season": "Kharif",
        "soilType": "Clayey",
        "nitrogen": 35.0,
        "phosphorous": 18.0,
        "potassium": 12.0,
        "temperature": 26.0,
        "humidity": 70.0,
        "moisture": 35.0,
    }
    response = client.post("/api/v1/fertilizer/ml-predict", json=payload)
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower()


def test_predict_invalid_soil(client):
    payload = {
        "crop": "rice",
        "season": "Kharif",
        "soilType": "MarsRegolith",
        "nitrogen": 35.0,
        "phosphorous": 18.0,
        "potassium": 12.0,
        "temperature": 26.0,
        "humidity": 70.0,
        "moisture": 35.0,
    }
    response = client.post("/api/v1/fertilizer/ml-predict", json=payload)
    assert response.status_code == 400
    assert "soil type" in response.json()["detail"].lower()


def test_predict_invalid_season(client):
    payload = {
        "crop": "rice",
        "season": "Autumn_Monsoon_Unknown",
        "soilType": "Clayey",
        "nitrogen": 35.0,
        "phosphorous": 18.0,
        "potassium": 12.0,
        "temperature": 26.0,
        "humidity": 70.0,
        "moisture": 35.0,
    }
    response = client.post("/api/v1/fertilizer/ml-predict", json=payload)
    assert response.status_code == 400
    assert "season" in response.json()["detail"].lower()


def test_predict_negative_nitrogen(client):
    payload = {
        "crop": "rice",
        "season": "Kharif",
        "soilType": "Clayey",
        "nitrogen": -10.0,
        "phosphorous": 18.0,
        "potassium": 12.0,
        "temperature": 26.0,
        "humidity": 70.0,
        "moisture": 35.0,
    }
    response = client.post("/api/v1/fertilizer/ml-predict", json=payload)
    assert response.status_code == 422


def test_predict_missing_field(client):
    payload = {
        "crop": "rice",
        "season": "Kharif",
        # missing soilType, NPK, temperature, etc.
    }
    response = client.post("/api/v1/fertilizer/ml-predict", json=payload)
    assert response.status_code == 422


def test_rule_based_fertilizer_guidance_unbroken(client):
    # Verify the existing API-based recommendation remains 100% functional
    response = client.get("/api/v1/fertilizers")
    assert response.status_code == 200
    catalog = response.json()
    assert len(catalog) > 0

    detail = client.get("/api/v1/fertilizers/npk-basal")
    assert detail.status_code == 200
