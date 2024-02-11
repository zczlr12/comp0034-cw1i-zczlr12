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
    AND a JSON object for Brand 1 Item 8 should be in the json
    """
    response = client.get("/items")
    assert response.headers["Content-Type"] == "application/json"
    item = {"brand_number": 1, "item_id": 8, "item_number": 8, "name": "B1_8"}
    assert item in response.json


def test_get_specified_data(client):
    """
    GIVEN a Flask test client
    WHEN a request is made to /items/5
    THEN the response json should contain the data for Brand 1 Item 5
    AND the response status_code should be 200
    """
    data_json = {'date': '2014-01-08T00:00:00',
                 'promotion': False, 'quantity': 3}
    response = client.get("/items/5")
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert data_json in response.json['data']


def test_get_item_not_exists(client):
    """
    GIVEN a Flask test client
    WHEN a request is made for a item id that does not exist
    THEN the response status_code should be 404 Not Found
    """
    response = client.get("/regions/200")
    assert response.status_code == 404


def test_post_item(client):
    """
    GIVEN a Flask test client
    AND valid JSON for a new item
    WHEN a POST request is made to /items
    THEN the response status_code should be 201
    """
    # JSON to create a new item
    item_json = {"brand_number": 5, "item_number": 1, "name": "B5_1"}
    # pass the JSON in the HTTP POST request
    response = client.post(
        "/items",
        json=item_json,
        content_type="application/json",
    )
    # 201 is the HTTP status code for a successful POST or PUT request
    assert response.status_code == 201
