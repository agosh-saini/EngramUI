import json
import time
import brainflow as bf
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds


from typing import List

class KnightBoard:
    def __init__(self, serial_port: str, channel_ids: List[int], gain: int = 12):
        """
        Initialize and configure the Knight Board.
        
        Args:
            serial_port: Serial port for the board connection.
            channel_ids: List of channel IDs to configure (e.g., [1, 2, 3, 7, 8]).
            gain: Gain setting (default 12).
        """
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port
        # Set gain override in other_info
        self.params.other_info = f'{{"gain": {gain}}}'
        self.channel_ids = channel_ids
        self.gain = gain

        # Initialize board
        self.board_shim = BoardShim(BoardIds.NEUROPAWN_KNIGHT_BOARD.value, self.params)
        self.board_id = self.board_shim.get_board_id()
        self.sampling_rate = self.board_shim.get_sampling_rate(self.board_id)

    def start_stream(self, buffer_size: int = 450000):
        """Start the data stream and configure specific channels."""
        if not self.board_shim.is_prepared():
            self.board_shim.prepare_session()

        # Knight Board requires stream to be running to accept commands
        self.board_shim.start_stream(buffer_size)
        print("Stream started.")
        time.sleep(2)

        try:
            print(f"Applying configuration for channels: {self.channel_ids}...")
            for x in self.channel_ids:
                time.sleep(0.5)
                # Channel Config
                cmd = f"chon_{x}_{self.gain}"
                print(f"sending {cmd}")
                self.board_shim.config_board(cmd)
                time.sleep(1)

                # RLD Config
                rld = f"rldadd_{x}"
                print(f"sending {rld}")
                self.board_shim.config_board(rld)
                time.sleep(0.5)
        except Exception as e:
            print(f"Error during board configuration: {e}")
            raise
        finally:
            print("Handshake complete.")

    def stop_stream(self):
        """Stop the data stream and release resources."""
        if hasattr(self, 'board_shim') and self.board_shim:
            try:
                if self.board_shim.is_prepared():
                    self.board_shim.stop_stream()
                    self.board_shim.release_session()
            except:
                pass
            self.board_shim = None
        print("Stream stopped and session released.")

    def get_board_data(self):
        """Get all data from the board."""
        if self.board_shim:
            return self.board_shim.get_board_data()
        return np.array([])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_stream()
