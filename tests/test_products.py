# GET /products
# Response expected: 200 OK, and a list 
def test_get_products_success(client):
    response = client.get('/products')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

# POST /products
# Response expected: 201 OK, JSON response
def test_create_product_success(client):
    new_product = {
        "name": "Test Product",
        "price": 19.99
    }

    response = client.post('/products', json=new_product)
    assert response.status_code == 201

    product = response.gt
