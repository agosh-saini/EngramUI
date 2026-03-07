# 🧠 EngramUI: Knight Board Interface

EngramUI provides a premium, high-performance interface for the **NeuroPawn Knight Board**, enabling real-time EEG data acquisition and AI-driven control.

---

## 🚀 Key Features

- **Robust Acquisition**: Automated handshake and configuration for the NeuroPawn Knight Board.
- **Reliable Streaming**: Integrated stability checks and error handling for continuous data flow.
- **Signal Integrity**: Native support for RLD (Right Leg Drive) and gain configuration (defaulting to 12).
- **Extensible Architecture**: Built on top of **BrainFlow** for cross-platform compatibility and high-fidelity sampling.

---

## 🛠 Getting Started

### 1. Installation

We recommend using a virtual environment. Install dependencies using `pip-tools` for deterministic builds:

```bash
# Set up venv (optional)
python -m venv venv
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install pip-tools
pip-sync requirements.txt
```

### 2. Run Visualization

To begin monitoring real-time activity (including EMG and EOG monitoring):

```bash
python main.py
```

*Note: The default serial port is currently set to `/dev/cu.usbserial-A5069RR4` in `main.py`.*

---

## 💻 Usage

### Importing the Interface

To integrate the Knight Board and the enhanced FFT processor into your own scripts:

```python
from EEG_Streaming import KnightBoard, EnhancedProcessor
import matplotlib.pyplot as plt

# Configuration
port = "/dev/cu.usbserial-A5069RR4"
data_channels = [1, 2, 3, 4]
ref_channels = [7, 8] # Combined ground and EOG reference

with KnightBoard(serial_port=port, channel_ids=data_channels + ref_channels) as board:
    board.start_stream()
    
    # Initialize the high-responsiveness processor
    processor = EnhancedProcessor(board, data_channels, ref_channels)
    
    plt.ion()
    plt.show()
    
    while processor.is_plot_active():
        data = board.get_board_data()
        if data.size > 0:
            processor.update_buffers(data)
            processor.process_and_plot()
        plt.pause(0.01)
```

---

## ⚙️ Technical Details

| Parameter | Default Value | Description |
| :--- | :--- | :--- |
| **Board ID** | `NEUROPAWN_KNIGHT_BOARD` (37) | BrainFlow board identifier. |
| **Gain** | 12 | Standard gain for the ADS1299-based amplifier. |
| **Channels** | 8 | Active EEG recording channels. |
| **Sampling Rate** | 250 Hz | Native sampling rate of the Knight Board. |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

Developed for use with the **[NeuroPawn Knight Board](https://github.com/NeuroPawn)**. Special thanks to the NeuroPawn team for providing the hardware interface specifications.
