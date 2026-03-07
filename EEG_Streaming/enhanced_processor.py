import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import detrend, windows, butter, iirnotch, filtfilt
import matplotlib.pyplot as plt

class EnhancedProcessor:
    def __init__(self, board, data_channels, ref_channels, notch_freq=60.0, lowcut=2.0, highcut=50.0, labels=None):
        """
        Initialize the enhanced stream processor with signal processing.
        
        Args:
            board: The KnightBoard instance.
            data_channels: Channels to process.
            ref_channels: List of channels to use as reference (average will be subtracted).
            notch_freq: Notch filter frequency (default 60Hz).
            lowcut: Lowcut for bandpass (default 2Hz).
            highcut: Highcut for bandpass (default 50Hz).
            labels: Dictionary mapping channel numbers to names.
        """
        assert board is not None, "Board instance is required"
        assert len(data_channels) > 0, "At least one data channel is required"
        assert isinstance(ref_channels, (list, tuple)), "ref_channels must be a list or tuple"
        assert len(ref_channels) > 0, "At least one reference channel is required"
        
        self.board = board
        self.data_channels = data_channels
        self.ref_channels = ref_channels
        self.sampling_rate = float(board.sampling_rate)
        # Use a 1-second window for maximum responsiveness (1.0Hz resolution)
        self.window_size = int(self.sampling_rate) 
        self.labels = labels or {}
        
        # Filter Settings
        self.lowcut = lowcut
        self.highcut = highcut
        self.notch_freq = notch_freq
        self.quality_factor = 30.0
        
        # Pre-compute filter coefficients (Butterworth 4th order)
        nyq = 0.5 * self.sampling_rate
        low = self.lowcut / nyq
        high = self.highcut / nyq
        self.b_band, self.a_band = butter(4, [low, high], btype='band')
        
        # Pre-compute notch filter coefficients
        self.b_notch, self.a_notch = iirnotch(self.notch_freq, self.quality_factor, self.sampling_rate)
        
        # Pre-allocate buffers for bounded memory behavior
        self.data_buffers = np.zeros((len(data_channels), self.window_size))
        self.ref_buffers = np.zeros((len(ref_channels), self.window_size))
        
        # Use Rectangular Window (no windowing) for maximum responsiveness 
        # and to avoid any temporal blurring/smoothing from tapering
        self.window = np.ones(self.window_size)
        self.window_sum = np.sum(self.window)
        assert self.window_sum > 0, "Window sum must be positive"
        
        # Setup Plotting
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.lines = []
        colors = ['#00ff00', '#ff00ff', '#00ffff', '#ffff00', '#0000ff', '#ff0000', '#ffffff', '#aaaaaa']
        
        for i, ch_num in enumerate(data_channels):
            # Highlight Ch 4 (EMG) and Ch 8 (EOG) as requested
            lw = 2.5 if ch_num in [4, 8] else 1.0
            alpha = 1.0 if ch_num in [4, 8] else 0.4
            label_text = self.labels.get(ch_num, f"Ch {ch_num}")
            
            line, = self.ax.plot([], [], color=colors[i % len(colors)], lw=lw, 
                                 label=label_text, alpha=alpha)
            self.lines.append(line)
            
        self.ax.set_xlim(0, 45)
        self.ax.set_ylim(0, 50)
        self.ax.set_title("Enhanced FFT (Detrended + Hamming Window)")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Amplitude (uV)")
        self.ax.legend(loc='upper right')
        self.ax.grid(True, alpha=0.15)
        plt.tight_layout()

    def update_buffers(self, data):
        """Update buffers with new board data."""
        assert data is not None, "Input data is None"
        assert len(data.shape) == 2, "Data must be 2D (channels x samples)"
        
        if data.size == 0:
            return
            
        n_samples = data.shape[1]
        assert n_samples >= 0, "Number of samples must be non-negative"
        
        # Update reference buffers
        for i, ref_ch in enumerate(self.ref_channels):
            ref_data = data[ref_ch, :]
            if n_samples >= self.window_size:
                self.ref_buffers[i, :] = ref_data[-self.window_size:]
            else:
                self.ref_buffers[i, :-n_samples] = self.ref_buffers[i, n_samples:]
                self.ref_buffers[i, -n_samples:] = ref_data

        # Update data buffers for each channel
        for i, _ in enumerate(self.data_channels):
            ch_num = self.data_channels[i]
            ch_data = data[ch_num, :]
            if n_samples >= self.window_size:
                self.data_buffers[i, :] = ch_data[-self.window_size:]
            else:
                self.data_buffers[i, :-n_samples] = self.data_buffers[i, n_samples:]
                self.data_buffers[i, -n_samples:] = ch_data

    def process_and_plot(self):
        """Perform re-referencing, detrending, windowing, and FFT."""
        assert self.window_size > 0, "Window size must be positive"
        assert self.sampling_rate > 0, "Sampling rate must be positive"
        
        xf = rfftfreq(self.window_size, 1 / self.sampling_rate)
        max_visible_amp = 0
        
        # Calculate average reference signal
        avg_ref = np.mean(self.ref_buffers, axis=0)
        
        for i in range(len(self.data_channels)):
            # 1. Software re-referencing (subtracting average of all refs)
            referenced_signal = self.data_buffers[i] - avg_ref
            
            # 2. Apply Filters (Notch then Bandpass)
            # Use filtfilt for zero-phase distortion
            notched = filtfilt(self.b_notch, self.a_notch, referenced_signal)
            filtered = filtfilt(self.b_band, self.a_band, notched)
            
            # 3. Detrend (remove DC offset and linear drift)
            detrended = detrend(filtered, type='linear')
            
            # 4. Apply Hamming Window
            windowed = detrended * self.window
            
            # 5. Compute Real FFT and scale for window coherent gain
            yf = rfft(windowed)
            amplitude = np.abs(yf) * 2.0 / self.window_sum
            
            # 6. Zero out 0-5 Hz range as requested
            amplitude[xf <= 5.0] = 0
            
            # 7. Smoothing removed as requested. Using raw amplitude.
            self.lines[i].set_data(xf, amplitude)
            
            # 8. Track max amplitude for auto-scaling
            visible_mask = (xf > 5.0) & (xf <= 45.0)
            if np.any(visible_mask):
                ch_max = np.max(amplitude[visible_mask])
                if ch_max > max_visible_amp:
                    max_visible_amp = ch_max

        self._apply_autoscaling(max_visible_amp)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def _apply_autoscaling(self, max_amp):
        """Apply instantaneous auto-scaling to the Y-axis for immediate feedback."""
        assert max_amp >= 0, "Maximum amplitude cannot be negative"
        assert self.ax is not None, "Plot axis must be initialized"
        
        # Immediate scaling: target with a floor of 10uV 
        # No temporal smoothing for fastest perception
        new_ylim = max(max_amp * 1.3, 10.0)
        self.ax.set_ylim(0, new_ylim)

    def is_plot_active(self):
        """Check if the plot window is still open."""
        assert self.fig is not None, "Plot figure must be initialized"
        # Removed strict member check to avoid race conditions
        return plt.fignum_exists(self.fig.number)
