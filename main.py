import pyaudio
import wave
import time
import sys
import math
import numpy as np
import threading
from matplotlib import pyplot as plt


def draw_plot(data):
    numpydata = np.fromstring(data, dtype=np.int16)

    monodata = numpydata[:(len(numpydata)-1)//2 + 1]

    i = 0
    while i < len(numpydata):
        monodata[i//2] = (numpydata[i] + numpydata[i+1])/2
        i += 2

    window = np.kaiser(STEREOCHUNK,8.5)
    fftdata = np.fft.rfft(monodata * window)
    fft_mag = np.abs(fftdata) * 2 / np.sum(window)
    fft_dbfs = 20 * np.log10(fft_mag/32768)
    # K = 120
    # fft_db = fft_dbfs + K
    line.set_ydata(fft_dbfs[minbin:CHUNK])
    plt.pause(0.00001)

STEREOCHUNK = 2048 * 2
CHUNK = STEREOCHUNK // 2

wf = wave.open("./assets/sound/bobble.wav", 'rb')

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(STEREOCHUNK)
numpydata = np.fromstring(data, dtype=np.int16)

figure = plt.figure()
sub_plot = figure.add_subplot(111)

freqbin_width = wf.getframerate()//STEREOCHUNK;

minbin = 10 // freqbin_width; 

plt.xscale('log')
plt.xlim(10,freqbin_width * CHUNK)
plt.xlabel('Hz')
plt.ylim(-120,0)
plt.ylabel('dB')

fakefft = [0] * (CHUNK-minbin)
line, = sub_plot.plot(fakefft)
line.set_xdata([x*freqbin_width for x in range(minbin,CHUNK)])

perf = time.perf_counter()

while data != '':

    # if time.perf_counter() - perf >= 1./120.:
    # print(perf)
    # perf = time.perf_counter()
    draw_plot(data)
    stream.write(data)
    data = wf.readframes(STEREOCHUNK)

stream.stop_stream()
stream.close()

p.terminate()
