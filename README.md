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

### 2. Verify Hardware

Before running the main application, verify your board connection and data quality:

```bash
python check_raw.py
```

*Note: Ensure your board is connected via USB. The default port is currently set to `/dev/cu.usbserial-A5069RR4`.*

---

## 💻 Usage

### Importing the Interface

To integrate the Knight Board into your own scripts, use the `KnightBoard` class from the `EEG_Streaming` module:

```python
from EEG_Streaming import KnightBoard
import time

# Initialize (Default: 8 channels, Gain 10)
port = "/dev/cu.usbserial-A5069RR4"
with KnightBoard(serial_port=port, num_channels=8) as board:
    board.start_stream()
    
    while True:
        data = board.get_board_data()
        if data.size > 0:
            print(f"Captured {data.shape[1]} samples")
        time.sleep(1)
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
