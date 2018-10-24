import services.audio_analyser as aa
from matplotlib import pyplot, animation


analyser = aa.analyser()

ydata,xdata = analyser.initialize("./assets/sound/mama.wav")

figure = pyplot.figure()
sub_plot = figure.add_subplot(111)

pyplot.xscale('log')
pyplot.xlim(analyser.minfreq,analyser.maxfreq)
pyplot.xlabel('Hz')
pyplot.ylim(-120,0)
pyplot.ylabel('dB')

line, = sub_plot.plot(xdata, ydata, linewidth=.5)

pyplot.pause(0.0001)

isOpen = True
def handle_close(evt):
    global isOpen
    isOpen = False

figure.canvas.mpl_connect('close_event', handle_close)

analyser.start()

while isOpen :
    line.set_ydata(analyser.get_freqdata())
    pyplot.pause(0.0001)
    # return [line,]

analyser.stop()
