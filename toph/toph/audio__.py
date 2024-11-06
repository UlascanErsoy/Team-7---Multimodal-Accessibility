import wave

import pyaudio

# Define the file path
filename = "ding.wav"

# Open the .wav file
wf = wave.open(filename, "rb")

# Instantiate PyAudio
p = pyaudio.PyAudio()

# Open stream with the correct output format
stream = p.open(
    format=p.get_format_from_width(wf.getsampwidth()),
    channels=wf.getnchannels(),
    rate=wf.getframerate(),
    output=True,
)


def play_chime():
    data = wf.readframes(1024)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)

    wf.rewind()


class AudibleRectangle:

    def __init__(self, rect):
        self.rect = rect
        self.press = None
        self.background = None

    def connect(self):
        """Connect to all the events we need."""
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            "button_press_event", self.on_press
        )

    def on_press(self, event):
        """Check whether mouse is over us; if so, store some data."""
        if event.inaxes != self.rect.axes:
            return
        contains, attrd = self.rect.contains(event)
        if not contains:
            return
        print("event contains", self.rect.xy)
        self.press = self.rect.xy, (event.xdata, event.ydata)

        play_chime()

    def disconnect(self):
        """Disconnect all callbacks."""
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
