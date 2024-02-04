import pyaudio
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time

class AudioAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Safe and Sound")

        # Frame setup
        self.frame = tk.Frame(master, padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)

        # Volume Display and Scale
        self.setup_volume_display_and_scale()

        # Graph Setup
        self.setup_graphs()

        # Warning Label
        self.warning_label = tk.Label(self.frame, text="", font=("Helvetica", 14), fg="red")
        self.warning_label.pack(side="bottom", pady=10)

        # Initialize variables for storing intervals exceeding 55dB
        self.high_noise_intervals = []
        self.high_noise_threshold = 55 # Set the threshold for high noise level

        # PyAudio Stream Setup
        self.setup_audio_stream()

        # For plotting
        self.reset_plotting_variables()

        # Start the volume update process
        self.update_volume()

    def setup_volume_display_and_scale(self):
        self.volume_label = tk.Label(self.frame, text="Real-time Volume (dB):", font=("Helvetica", 14))
        self.volume_label.pack()
        
        self.volume_value_label = tk.Label(self.frame, text="", font=("Helvetica", 10))
        self.volume_value_label.pack(pady=(0, 10))
        
        self.scale_canvas = tk.Canvas(self.frame, width=300, height=50, bg="white")
        self.scale_canvas.pack(pady=(0, 20))

    def setup_graphs(self):
        self.fig = Figure(figsize=(9, 5.5), dpi=100)
        self.ax1 = self.fig.add_subplot(211)  # For continuous volume graph
        self.ax2 = self.fig.add_subplot(212)  # For strip band graph
        self.ax1.set_ylabel('Volume (dB)')
        self.ax2.set_xlabel('Interval (10s)')
        self.ax2.set_ylabel('Average Volume (dB)')
        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.graph_canvas.get_tk_widget().pack()

    def setup_audio_stream(self):
        self.chunk_size = 1024
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=self.chunk_size
        )

    def reset_plotting_variables(self):
        self.start_time = time.time()
        self.interval_start_time = self.start_time
        self.time_points = []
        self.volume_points = []
        self.interval_volumes = []

    def update_volume(self):
        data = self.stream.read(self.chunk_size, exception_on_overflow=False)
        audio_np = np.frombuffer(data, dtype=np.int16)
        amplitude = np.abs(audio_np).mean()
        volume_dB = 20 * np.log10(amplitude) + 30 if amplitude > 0 else 0

        # Continuous graph update
        elapsed_time = time.time() - self.start_time
        self.time_points.append(elapsed_time)
        self.volume_points.append(volume_dB)
        self.volume_value_label.config(text=f"{volume_dB:.2f} dB")

        # Interval graph update
        self.interval_volumes.append(volume_dB)
        if time.time() - self.interval_start_time >= 10:
            avg_volume = np.mean(self.interval_volumes)
            self.ax2.bar(len(self.ax2.patches), avg_volume, width=0.8, color='blue', align='center')
            self.interval_start_time = time.time()
            self.interval_volumes = []

            # Check for warning
            if avg_volume > self.high_noise_threshold:
                # Add the interval to the list of high noise intervals
                self.high_noise_intervals.append(len(self.high_noise_intervals) + 1)

                # Update the warning message with the list of high noise intervals
                warning_msg = f"Warning! The noise level exceeds {self.high_noise_threshold}dB in the following intervals: {', '.join(map(str, self.high_noise_intervals))}\nPossible solutions: Improve traffic flow, limit heavy vehicles, promote electric vehicles, increase noise pollution awareness\nPossible consequences: Hearing loss, sleep disturbance, cardiovascular issues, mental health problems, impaired learning, premature death"
                self.warning_label.config(text=warning_msg)

        # Update scale
        self.update_scale(volume_dB)

        # Redraw graphs
        self.redraw_graphs()

        self.master.after(100, self.update_volume)

    def update_scale(self, volume_dB):
        # Implement the scale update logic here, as per your requirements
        if 0 < volume_dB <= 11.25:  # Quiet
            color = "darkgreen"
            width = 12.5
        elif 11.25 < volume_dB <= 22.5: 
            color = "green"
            width = 25
        elif 22.5 < volume_dB <= 33.75: 
            color = "green"
            width = 37.5
        elif 33.75 < volume_dB <= 45: 
            color = "greenyellow"
            width = 50
        elif 45 < volume_dB <= 48.75: 
            color = "yellow"
            width = 75
        elif 48.75 < volume_dB <= 52.5:  
            color = "yellow"
            width = 100
        elif 52.5 < volume_dB <= 56.25:  
            color = "yellow"
            width = 125
        elif 56.25 < volume_dB <= 60:  
            color = "orange"
            width = 150
        elif 45 < volume_dB <= 60:  
            color = "orange"
            width = 150
        elif 60 < volume_dB <= 70: 
            color = "red"
            width = 200
        elif 70 < volume_dB <= 80: 
            color = "red"
            width = 250
        elif 80 < volume_dB <= 90: 
            color = "darkred"
            width = 300
        else:  # Loud
            color = "darkred"
            width = 350

        self.scale_canvas.delete("all")  # Clear existing scale
        self.scale_canvas.create_rectangle(0, 0, width, 50, fill=color, outline=color)

    def redraw_graphs(self):
        self.ax1.clear()
        self.ax1.plot(self.time_points, self.volume_points, label='Volume (dB)')
        self.ax1.legend(loc="upper right")
        elapsed_time = time.time() - self.start_time
        self.ax1.set_xlim(left=max(0, time.time() - self.start_time - 60), right=elapsed_time)

        self.graph_canvas.draw()

    def on_closing(self):
        print("Stopping analysis.")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.master.destroy()

def main():
    root = tk.Tk()
    app = AudioAnalyzerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.geometry("800x800") # Adjust size as needed for the new layout
    root.mainloop()

if __name__ == "__main__":
    main()
