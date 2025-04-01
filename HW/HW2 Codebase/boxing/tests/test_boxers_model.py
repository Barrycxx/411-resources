import pytest
import boxing.models.boxers_model as boxer_model
from unittest.mock import MagicMock

# This fixture is used to mock the database connection
@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.Mock()  # Mocking the database connection
    mock_cursor = mocker.Mock()  # Mocking the database cursor
    mock_conn.cursor.return_value = mock_cursor  # The connection's cursor method returns the mock cursor
    
    mock_cursor.fetchone.return_value = None  # When fetchone is called, return None (no data)
    mock_cursor.fetchall.return_value = []  # When fetchall is called, return an empty list
    mock_conn.commit.return_value = None  # Mocking the commit method, which returns None
    
    # Ensure that the mock connection supports 'with' statements
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)  # Mocking __enter__ method
    mock_conn.__exit__ = MagicMock(return_value=None)  # Mocking __exit__ method
    
    # Patch the actual database connection with our mock
    mocker.patch("boxing.models.boxers_model.get_db_connection", return_value=mock_conn)
    return mock_cursor


def test_create_boxer_success(mock_db_connection):
    """Test the functionality of creating a boxer"""
    boxer_model.create_boxer("Ali", 180, 70, 72.5, 28)
    
    insert_query = "INSERT INTO boxers (name, weight, height, reach, age)"
    call_args = mock_db_connection.execute.call_args[0][0]  # Get the first argument passed to execute
    assert insert_query in call_args  # Ensure the insert query is correct


def test_create_boxer_duplicate_name(mock_db_connection):
    """Test creating a boxer with a duplicate name"""
    mock_db_connection.fetchone.return_value = True  # Simulate that the boxer already exists
    with pytest.raises(ValueError, match="already exists"):
        boxer_model.create_boxer("Ali", 180, 70, 72.5, 28)


def test_get_boxer_by_id_success(mock_db_connection):
    """Test retrieving a boxer by ID"""
    mock_db_connection.fetchone.return_value = (1, "Ali", 180, 70, 72.5, 28)
    boxer = boxer_model.get_boxer_by_id(1)
    
    # Verify that the boxer's data is correct
    assert boxer.name == "Ali"
    assert boxer.weight == 180
    assert boxer.age == 28


def test_get_boxer_by_id_not_found(mock_db_connection):
    """Test the scenario where a boxer is not found by ID"""
    mock_db_connection.fetchone.return_value = None  # Simulate no boxer found
    with pytest.raises(ValueError, match="not found"):
        boxer_model.get_boxer_by_id(999)
