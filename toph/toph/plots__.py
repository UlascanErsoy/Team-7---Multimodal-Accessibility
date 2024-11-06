import matplotlib.pyplot as plt

from toph.audio import play_chime


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


class Figure:

    def show(self):
        """ """
        self.play()
        plt.show()

    def play(self):
        """ """
        for rect in self.rects:
            play_chime()


class BarFigure(Figure):

    def __init__(self, x, y):
        self.x = x
        self.y = y

        fig, ax = plt.subplots()
        self.rects = ax.bar(x, y)
        drs = []
        for rect in self.rects:
            dr = AudibleRectangle(rect)
            dr.connect()
            drs.append(dr)


def bar(x, y) -> BarFigure:
    return BarFigure(x, y)
