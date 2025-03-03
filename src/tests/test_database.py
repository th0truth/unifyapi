from unittest.mock import patch, AsyncMock

@patch("motor.motor_asyncio.AsyncIOMotorClient")
async def test_find_by(mock_client):
    # Mock the database and collection
    mock_db, mock_collection = AsyncMock(), AsyncMock()

    # Set up the mock client
    mock_client.return_value.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    mock_collection.find_one.return_value = {"edbo_id": 1515}
