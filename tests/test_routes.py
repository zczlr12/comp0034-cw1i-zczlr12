def test_get_items_status_code(client):
    """
    GIVEN a Flask test client
    WHEN a request is made to /items
    THEN the status code should be 200
    """
    response = client.get("/items")
    assert response.status_code == 200


def test_get_items_json(client):
    """
    GIVEN a Flask test client
    AND the database contains data of the items
    WHEN a request is made to /items
    THEN the response should contain json
    AND a JSON object for Tonga should be in the json
    """
    response = client.get("/items")
    assert response.headers["Content-Type"] == "application/json"
    item = {"brand_number": 1, "item_id": 8, "item_number": 8, "name": "B1_8"}
    assert item in response.json
