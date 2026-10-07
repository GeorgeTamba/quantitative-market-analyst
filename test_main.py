from fastapi.testclient import TestClient
from main import app

# Create a dummy client to simulate a frontend making requests
client = TestClient(app)

def test_get_top_coins_success():
    """Test that the top-coins endpoint returns a valid 200 response and JSON data."""
    response = client.get("/api/top-coins?limit=5")
    
    # 1. Check if the server responded successfully
    assert response.status_code == 200
    
    # 2. Check if the data is formatted correctly
    data = response.json()
    assert "coins" in data
    
    # 3. Check if our limit parameter worked
    assert len(data["coins"]) == 5
    
    # 4. Check if the first coin has the correct data structure
    first_coin = data["coins"][0]
    assert "symbol" in first_coin
    assert "price_usd" in first_coin