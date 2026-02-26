import json
import time
import brainflow as bf
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds


class KnightBoard:
    def __init__(self, serial_port: str, num_channels: int = 8, gain: int = 10):
        """Initialize and configure the Knight Board."""
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port
        # optional: set gain override (default 12)
        self.params.other_info = '{"gain": 6}'
        self.num_channels = num_channels
        self.gain = gain # Defaulting to 12 as per test_default.py chon commands

        # Initialize board
        self.board_shim = BoardShim(BoardIds.NEUROPAWN_KNIGHT_BOARD.value, self.params)
        self.board_id = self.board_shim.get_board_id()
        self.eeg_channels = self.board_shim.get_exg_channels(self.board_id)
        self.sampling_rate = self.board_shim.get_sampling_rate(self.board_id)

    def start_stream(self, buffer_size: int = 450000):
        """
        Start the data stream and configure channels.
        """
        if not self.board_shim.is_prepared():
            self.board_shim.prepare_session()

        # Knight Board requires stream to be running to accept commands
        self.board_shim.start_stream(buffer_size)
        print("Stream started.")
        time.sleep(2)

        try:
            print(f"Applying configuration for {self.num_channels} channels...")
            for x in range(1, self.num_channels + 1):
                time.sleep(0.5)
                # Channel Config - matching hardcoded 12 from test_default.py
                cmd = f"chon_{x}_12"
                print(f"sending {cmd}")
                self.board_shim.config_board(cmd)
                time.sleep(1)

                # RLD Config
                rld = f"rldadd_{x}"
                print(f"sending {rld}")
                self.board_shim.config_board(rld)
                time.sleep(0.5)

        finally:
            print("Handshake complete.")

    def stop_stream(self):
        """Stop the data stream and release resources."""
        if self.board_shim.is_prepared():
            try:
                self.board_shim.stop_stream()
            except:
                pass
            self.board_shim.release_session()
            print("Stream stopped.")

    def get_board_data(self):
        """Get all data from the board."""
        return self.board_shim.get_board_data()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_stream()
