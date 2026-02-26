import time
import numpy as np
from EEG_Streaming import KnightBoard

def main():
    port = "/dev/cu.usbserial-A5069RR4"
    print(f"Checking raw values on {port}...")
    
    # Initialize with 8 channels and gain 10
    board = KnightBoard(serial_port=port, num_channels=8, gain=10)
    
    try:
        board.start_stream()
        print("\nReadout started. Printing first 5 samples of EEG channels when data arrives.")
        print("EEG Channels Indices:", board.eeg_channels)
        
        start_time = time.time()
        while time.time() - start_time < 30: # Check for 30 seconds
            data = board.get_board_data()
            
            if data.size > 0:
                # Extract EEG channels
                eeg_data = data[board.eeg_channels]
                num_samples = eeg_data.shape[1]
                
                print(f"\n--- Captured {num_samples} samples ---")
                print("Full first sample (all 13 rows):")
                print(data[:, 0])
                
                # Check for all zeros in EEG channels (1-8)
                if np.all(eeg_data == 0):
                    print("WARNING: All EEG values are exactly ZERO.")
                else:
                    print(f"Mean: {np.mean(eeg_data):.2f}, Std: {np.std(eeg_data):.2f}")
                    
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        board.stop_stream()

if __name__ == "__main__":
    main()
