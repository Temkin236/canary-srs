import json
import os

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/accuracy", tags=["Accuracy & Evaluation"])

EVALUATION_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "data",
        "accuracy",
        "latest_evaluation.json",
    )
)


@router.get("/latest")
def get_latest_accuracy_evaluation():
    """
    Returns the real measured accuracy and benchmark evaluation artifact (FR-45).
    If the evaluation script has not been run, returns a 404 with instructions.
    """
    if not os.path.exists(EVALUATION_PATH):
        raise HTTPException(
            status_code=404,
            detail=(
                "Evaluation results are not available yet. "
                "Run 'uv run python scripts/evaluate.py' to generate benchmark artifacts."
            ),
        )

    try:
        with open(EVALUATION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read evaluation artifact: {e}",
        )
