# AUTHENTICATION ROUTES
def test_register_success(client, random_user_json):
    """
    GIVEN a valid format account attributes for a user not already registered
    WHEN an account is created
    THEN the status code should be 201
    """
    user_register = client.post('/register', json=random_user_json,
                                content_type="application/json")
    assert user_register.status_code == 201


def test_register_fail(client, random_user_json):
    """
    GIVEN a valid format account attributes for a user not already registered
    WHEN an account is created
    THEN the status code should be 409
    """
    client.post('/register', json=random_user_json,
                content_type="application/json")
    user_register = client.post('/register', json=random_user_json,
                                content_type="application/json")
    assert user_register.status_code == 409


def test_login_success(client, new_user):
    """
    GIVEN a valid format username and password for a user already registered
    WHEN /login is called
    THEN the status code should be 201
    """
    user_register = client.post('/login', json=new_user,
                                content_type="application/json")
    assert user_register.status_code == 201


def test_login_fail(client):
    """
    GIVEN a valid format username and password for a user not registered
    WHEN /login is called
    THEN the status code should be 401
    """
    user_json = {"username": "test", "password": "abcdefg"}
    user_login = client.post('/login', json=user_json,
                             content_type="application/json")
    assert user_login.status_code == 401


# COMMENT ROUTES
def test_get_comments_status_code(client):
    """
    GIVEN a Flask test client
    WHEN a request is made to /comments
    THEN the status code should be 200
    """
    response = client.get("/comments")
    assert response.status_code == 200


def test_get_comments_json(client):
    """
    GIVEN a Flask test client
    AND the database contains no comments
    WHEN a request is made to /comments
    THEN the response should be an empty list
    """
    response = client.get("/comments")
    assert response.headers["Content-Type"] == "application/json"
    assert response.json == []


def test_user_not_logged_in_cannot_post_comment(client, comment_json):
    """
    GIVEN a user that is not logged in
    AND a route that is protected by login
    WHEN a POST request to /comments is made
    THEN the HTTP response status code should be 401 with the following message
    'Authentication Token missing'
    """
    response = client.post("/comments", json=comment_json)
    assert response.status_code == 401
    assert response.json['message'] == 'Authentication Token missing'
    

def test_user_logged_in_post_comment(client, login, comment_json):
    """
    GIVEN a registered user that is successfully logged in
    AND a route that is protected by login
    WHEN a POST request to /comments is made
    THEN a new comment can be posted
    THEN the HTTP status code should be 200
    """
    # pass the token in the headers of the HTTP request
    headers = {
        'content-type': "application/json",
        'Authorization': login['token']
    }
    response = client.post("/comments", json=comment_json, headers=headers)
    assert response.status_code == 200


# ITEM ROUTES
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
    response = client.get("/items/200")
    assert response.status_code == 404


def test_post_item(client, login):
    """
    GIVEN a Flask test client
    AND valid JSON for a new item
    WHEN a POST request is made to /items
    THEN the response status_code should be 201
    """
    # JSON to create a new item
    item_json = {"brand_number": 5, "item_number": 1, "name": "B5_1"}
    # pass the token in the headers of the HTTP request
    headers = {
        'content-type': "application/json",
        'Authorization': login['token']
    }
    # pass the JSON in the HTTP POST request
    response = client.post(
        "/items",
        json=item_json,
        headers=headers
    )
    assert response.status_code == 200


def test_item_post_error(client, login):
    """
        GIVEN a Flask test client
        AND JSON for a new item that is missing a required field ("name")
        WHEN a POST request is made to /items
        THEN the response status_code should be 400
        """
    # JSON to create a new item
    missing_item_json = {"brand_number": 5, "item_number": 1}
    # pass the token in the headers of the HTTP request
    headers = {
        'content-type': "application/json",
        'Authorization': login['token']
    }
    # pass the JSON in the HTTP POST request
    response = client.post(
        "/items",
        json=missing_item_json,
        headers=headers
    )
    assert response.status_code == 400


def test_delete_item(client, login):
    """
    GIVEN an existing item in JSON format
    AND a Flask test client
    WHEN a DELETE request is made to /items/8
    THEN the response status code should be 200
    AND the response content should include following message
    'The item with id 8 has been deleted.'
    """
    headers = {
        'content-type': "application/json",
        'Authorization': login['token']
    }
    response = client.delete("/items/8", headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'The item with id 8 has been deleted'


def test_delete_item_not_exists(client, login):
    """
    GIVEN a Flask test client
    WHEN a DELETE request is made to an item that does not exist /items/200
    THEN the response status code should be 404
    AND the response content should include the following error message
    '404 Not Found: Item not found.'
    """
    headers = {
        'content-type': "application/json",
        'Authorization': login['token']
    }
    response = client.delete("/items/200", headers=headers)
    assert response.status_code == 404
    assert response.json['error'] == '404 Not Found: Item not found.'


def test_user_not_logged_in_cannot_edit_item(client):
    """
    GIVEN a user that is not logged in
    AND a route that is protected by login
    AND an item that can be edited
    WHEN a PATCH request to /items/8 is made
    THEN the HTTP response status code should be 401 with the following message
    'Authentication Token missing'
    """
    new_name = {'name': 'pizza'}
    response = client.patch("/items/8", json=new_name)
    assert response.status_code == 401
    assert response.json['message'] == 'Authentication Token missing'


def test_user_logged_in_user_can_edit_item(client, login):
    """
    GIVEN a user that is successfully logged in
    AND a route that is protected by login
    AND an item that can be edited
    WHEN a PATCH request to /items/3 is made
    THEN the HTTP status code should be 200
    AND the response content should include the following message
    'Item with id 8 updated.'
    """
    # pass the token in the headers of the HTTP request
    token = login['token']
    headers = {
        'content-type': "application/json",
        'Authorization': token
    }
    new_name = {'name': 'pizza'}
    response = client.patch("/items/3", json=new_name, headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Item with id 3 updated."}
