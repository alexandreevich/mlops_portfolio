from fastapi.testclient import TestClient
from main import app


# def test_one():
#     assert True


# def test_two():
#     assert 1 == 1


client = TestClient(app)


def test_predict_valid_item():
    # Используй существующий itemid из item_features
    response = client.get(
        "/predict_purchase", params={"itemid": 98113, "hour": 14, "weekday": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert "purchase_probability" in data
    assert 0 <= data["purchase_probability"] <= 1


def test_predict_invalid_item():
    response = client.get(
        "/predict_purchase", params={"itemid": 999999, "hour": 12, "weekday": 3}
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "item not found"
