import pytest
import boxing.models.boxer_model as boxer_model
from dataclasses import asdict
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    mocker.patch("boxing.models.boxer_model.get_db_connection", return_value=mock_conn)
    return mock_cursor


def test_create_boxer_success(mock_db_connection):
    boxer_model.create_boxer("Ali", 180, 70, 72.5, 28)
    insert_query = "INSERT INTO boxers (name, weight, height, reach, age)"
    call_args = mock_db_connection.execute.call_args[0][0]
    assert insert_query in call_args


def test_create_boxer_duplicate_name(mock_db_connection):
    mock_db_connection.fetchone.return_value = True
    with pytest.raises(ValueError, match="already exists"):
        boxer_model.create_boxer("Ali", 180, 70, 72.5, 28)


def test_get_boxer_by_id_success(mock_db_connection):
    mock_db_connection.fetchone.return_value = (1, "Ali", 180, 70, 72.5, 28)
    boxer = boxer_model.get_boxer_by_id(1)
    assert boxer.name == "Ali"
    assert boxer.weight == 180
    assert boxer.age == 28


def test_get_boxer_by_id_not_found(mock_db_connection):
    mock_db_connection.fetchone.return_value = None
    with pytest.raises(ValueError, match="not found"):
        boxer_model.get_boxer_by_id(999) 