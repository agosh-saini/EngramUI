import time
import matplotlib.pyplot as plt
from EEG_Streaming.knight_board import KnightBoard
from EEG_Streaming.enhanced_processor import EnhancedProcessor

def main():
    # Configuration
    SERIAL_PORT = "/dev/cu.usbserial-A5069RR4"
    # User specified: Ch 4 is Throat EMG
    DATA_CHANNELS = [1, 2, 3, 4] 
    REF_CHANNELS = [7, 8] # Channel 8 now used to account for EOG artifacts
    NOTCH_FREQ = 60.0
    
    # Human-readable labels for specific channels
    CHANNEL_LABELS = {
        4: "EMG (Throat)",
        8: "EOG (Artifact)"
    }
    
    # Initialize the board
    all_channels = DATA_CHANNELS + REF_CHANNELS
    board = KnightBoard(SERIAL_PORT, all_channels)
    
    try:
        board.start_stream()
        
        # Initialize the processor with 1-second window for maximum responsiveness
        processor = EnhancedProcessor(board, DATA_CHANNELS, REF_CHANNELS, 
                                     notch_freq=NOTCH_FREQ, 
                                     labels=CHANNEL_LABELS)
        
        print(f"Sampling Rate: {board.sampling_rate}Hz")
        print(f"Filter Pipeline: 2-50Hz Bandpass + {NOTCH_FREQ}Hz Notch")
        print(f"Processing: Detrending + Instant Auto-scaling (Fast Reaction)")
        print(f"Referencing: Subtracting Average of {REF_CHANNELS} from {DATA_CHANNELS}")
        print("Starting visualization... Close window or press Ctrl+C to stop.")
        
        plt.ion()
        plt.show()

        while processor.is_plot_active():
            # Get data from the board
            data = board.get_board_data()
            
            if data.size > 0:
                processor.update_buffers(data)
                processor.process_and_plot()
            
            # Short pause for UI updates
            plt.pause(0.01)
            
    except KeyboardInterrupt:
        print("\nInterrupt received, stopping...")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        plt.close('all')
        board.stop_stream()
        print("System shutdown complete.")

if __name__ == "__main__":
    main()
