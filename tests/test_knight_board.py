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
    board = KnightBoard(serial_port="COM3", channel_ids=[1, 2, 3, 7, 8], gain=10)
    assert board.channel_ids == [1, 2, 3, 7, 8]
    mock_board_shim.assert_called_once()


def test_knight_board_start_stream(mock_board_shim):
    instance = mock_board_shim.return_value
    instance.is_prepared.return_value = False

    board = KnightBoard(serial_port="COM3", channel_ids=[1, 2, 8], gain=12)

    # Mocking sleep to speed up tests
    with patch("time.sleep", return_value=None):
        board.start_stream()

    assert instance.prepare_session.called
    assert instance.start_stream.call_count == 1
    # Check if config_board was called for each channel (chon and rld)
    # len([1, 2, 8]) = 3 channels. Each gets chon and rld. 3 * 2 = 6 calls.
    assert instance.config_board.call_count == 6


def test_knight_board_stop_stream(mock_board_shim):
    instance = mock_board_shim.return_value
    instance.is_prepared.return_value = True

    board = KnightBoard(serial_port="COM3", channel_ids=[1])
    board.stop_stream()

    assert instance.stop_stream.called
    assert instance.release_session.called
