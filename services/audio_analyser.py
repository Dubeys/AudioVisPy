import pyaudio
import wave
import numpy as np
import threading

class analyser :
    def __init__(self, chunk_size=4096, lowfreq_limit=10) :

        self.STEREOCHUNK = chunk_size
        self.CHUNK = chunk_size // 2

        self.minbin = 2
        self.maxbin = self.CHUNK
        
        self.canplay = False

        # self.window = np.kaiser(self.STEREOCHUNK, 2)
        self.window = np.blackman(self.STEREOCHUNK)

        self.lock = threading.Lock()

    def initialize(self, url) :

        self.file = wave.open(url, 'rb')
        self.pyaudio = pyaudio.PyAudio()

        sampleformat = self.pyaudio.get_format_from_width(self.file.getsampwidth())
        channels = self.file.getnchannels()
        rate = self.file.getframerate()

        freqbin_width = rate // self.STEREOCHUNK

        self.minfreq = self.minbin * freqbin_width
        self.maxfreq = self.maxbin * freqbin_width

        self.stream = self.pyaudio.open(format= sampleformat,
                                        channels= channels,
                                        rate= rate,
                                        output=True)

        self.data = self.file.readframes(self.STEREOCHUNK)

        return self.get_freqdata(), np.linspace(self.minfreq,self.maxfreq,self.CHUNK - self.minbin)

    def start(self) : 
        if self.canplay : return

        self.canplay = True
        self.thread = threading.Thread(target=self.play)
        self.thread.start()

    def stop(self) :
        self.lock.acquire()
        self.canplay = False
        self.lock.release()
        self.thread.join()
        self.terminate()

    def terminate(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

    def play(self) :

        while self.canplay :

            self.nextframe()

            if self.data == '':
                self.lock.acquire()
                self.canplay = False
                self.lock.release()


    def nextframe(self):

        self.stream.write(self.data)
        self.lock.acquire()
        self.data = self.file.readframes(self.STEREOCHUNK)
        self.lock.release()

    def get_freqdata(self):

        self.lock.acquire()
        npdata = np.fromstring(self.data, dtype=np.int16)
        self.lock.release()

        monodata = np.empty( len(npdata)//2 )

        i = 0
        while i < len(npdata):
            monodata[i//2] = (float(npdata[i]) + float(npdata[i+1])) * 0.5
            i += 2

        fftdata = np.fft.rfft(monodata * self.window)
        fft_mag = np.abs(fftdata) * 2 / np.sum(self.window)
        fft_dbfs = 20 * np.log10(fft_mag/32768)
        # K = 120
        # fft_db = fft_dbfs + K

        return fft_dbfs[self.minbin:self.CHUNK]
