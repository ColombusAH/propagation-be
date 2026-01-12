import pytest
from app.db.dependencies import get_db
from unittest.mock import MagicMock, patch, PropertyMock
from fastapi import HTTPException, Request

@pytest.mark.asyncio
async def test_get_db_state_missing():
    """Test get_db when prisma is missing from app state."""
    mock_request = MagicMock(spec=Request)
    # Using a spec without 'prisma' ensures AttributeError on access
    mock_request.app = MagicMock()
    mock_request.app.state = MagicMock(spec=[]) 
    
    with pytest.raises(HTTPException) as exc:
        await get_db(mock_request)
    assert exc.value.status_code == 503

@pytest.mark.asyncio
async def test_get_db_unexpected_error():
    """Test get_db with unexpected exception."""
    mock_request = MagicMock(spec=Request)
    mock_app = MagicMock()
    # Accessing .prisma will return a wrapper that raises error on .client
    mock_wrapper = MagicMock()
    type(mock_wrapper).client = PropertyMock(side_effect=Exception("Boom"))
    mock_app.state.prisma = mock_wrapper
    mock_request.app = mock_app
    
    with pytest.raises(HTTPException) as exc:
        await get_db(mock_request)
    assert exc.value.status_code == 500
