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
    GIVEN a valid format username and password for a user not already registered
    WHEN /login is called
    THEN the status code should be 401
    """
    user_json = {"username": "test", "password": "abcdefgh"}
    user_register = client.post('/login', json=user_json,
                                content_type="application/json")
    assert user_register.status_code == 401


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
    

def test_post_comment(client, login, comment_json):
    """
    GIVEN a registered user that is successfully logged in
    AND a route that is protected by login
    AND a new Comment that can be posted
    WHEN a POST request to /comments is made
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
