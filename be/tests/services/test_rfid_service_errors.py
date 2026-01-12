import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService

@pytest.mark.asyncio
async def test_process_tag_db_error():
    """Test _process_tag when database error occurs during commit."""
    service = RFIDReaderService()
    tag_data = {"epc": "ERROR-TAG", "rssi": -50.0}
    
    # We need to patch SessionLocal where it's used
    with patch("app.services.rfid_reader.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        # Mocking query to return a mock tag
        mock_db.query().filter().first.return_value = None
        
        # Make commit raise exception
        mock_db.commit.side_effect = Exception("Commit Failed")
        
        await service._process_tag(tag_data)
        
        # Verify rollback was called
        assert mock_db.rollback.called
