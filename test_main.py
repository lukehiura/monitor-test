from fastapi.testclient import TestClient
from main import (
    app,
    Item,
)  # make sure to replace 'main' with your actual file name if different
from fastapi import HTTPException
import warnings
import logging

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Set up a logger for warnings
logger = logging.getLogger("warnings")
logger.setLevel(logging.WARNING)


# Create a custom handler for the logger
class WarningHandler(logging.Handler):
    def emit(self, record):
        logging.warning(record.getMessage())


# Add the custom handler to the logger
logger.addHandler(WarningHandler())


client = TestClient(app)


def test_create_item():
    # Test creating an item
    response = client.post(
        "/items/", json={"name": "Foo", "price": 123.0, "quantity": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Foo"
    assert data["price"] == 123.0
    assert data["quantity"] == 3


def test_create_item_already_exists():
    # Test creating an item that already exists
    client.post("/items/", json={"name": "Foo", "price": 123.0, "quantity": 3})
    response = client.post(
        "/items/", json={"name": "Foo", "price": 456.0, "quantity": 4}
    )
    assert response.status_code == 400


def test_read_item():
    # Test reading an item
    client.post("/items/", json={"name": "Bar", "price": 123.0, "quantity": 3})
    response = client.get("/items/Bar")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bar"
    assert data["price"] == 123.0
    assert data["quantity"] == 3


def test_read_item_not_found():
    # Test reading an item that doesn't exist
    response = client.get("/items/Baz")
    assert response.status_code == 404


def test_divide_by_zero():
    # Test divide by zero error
    with warnings.catch_warnings(record=True) as warning_records:
        response = client.get("/divide-by-zero")
        assert response.status_code == 400
        assert "Division by zero error" in response.json()["detail"]

        # Log the warnings
        for warning_record in warning_records:
            logger.warning(warning_record.message)


def test_key_error():
    # Test key error
    with warnings.catch_warnings(record=True) as warning_records:
        response = client.get("/key-error")
        assert response.status_code == 400
        assert "Key error" in response.json()["detail"]

        # Log the warnings
        for warning_record in warning_records:
            logger.warning(warning_record.message)
