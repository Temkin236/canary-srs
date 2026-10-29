from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_latest_accuracy_evaluation():
    resp = client.get("/api/v1/accuracy/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert "metrics" in data
    assert "confusion_matrix" in data
    assert "tpr" in data["metrics"]
    assert "fpr" in data["metrics"]
    assert "tpr_ci_lower" in data["metrics"]
    assert "fpr_ci_upper" in data["metrics"]
    assert data["sample_size"] > 0
    assert "notice" in data
