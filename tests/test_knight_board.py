import pytest
from unittest.mock import patch
from EEG_Streaming.knight_board import KnightBoard


@pytest.fixture
def mock_board_shim():
    with patch("EEG_Streaming.knight_board.BoardShim") as mock:
        instance = mock.return_value
        instance.is_prepared.return_value = False
        instance.get_board_data_count.return_value = 0
        yield mock


def test_knight_board_init(mock_board_shim):
    board = KnightBoard(serial_port="COM3", num_channels=8, gain=10)
    assert board.num_channels == 8
    mock_board_shim.assert_called_once()


def test_knight_board_start_stream(mock_board_shim):
    instance = mock_board_shim.return_value
    instance.is_prepared.return_value = False

    board = KnightBoard(serial_port="COM3", num_channels=8, gain=10)

    # Mocking sleep to speed up tests
    with patch("time.sleep", return_value=None):
        board.start_stream()

    assert instance.prepare_session.called
    assert (
        instance.start_stream.call_count == 2
    )  # Once at start, once after config restart
    assert instance.stop_stream.called
    # Check if config_board was called for each channel (chon and rld)
    assert instance.config_board.call_count == 16


def test_knight_board_stop_stream(mock_board_shim):
    instance = mock_board_shim.return_value
    instance.is_prepared.return_value = True
    instance.get_board_data_count.return_value = 1

    board = KnightBoard(serial_port="COM3", num_channels=8)
    board.stop_stream()

    assert instance.stop_stream.called
    assert instance.release_session.called
