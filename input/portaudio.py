# -*- coding: utf-8 -*-
# @Author  : lucius
# @Email   : cnotperfect@foxmail.com


"""
使用WASAPI环回捕获记录声卡输出。
使用了 <https://github.com/intxcc/pyaudio_portaudio>
这个东东扩展了pyaudio_portaudio，使pyaudio初始化流时支持as_loopback.
"""

import collections
import threading
import pyaudio

class Portrecorder(object):
    """
    使用pyaudio记录音频到buffer
    """

    def __init__(self, name, chunks, chunksize=1024, channels=2, rate="auto",in_out=None):
        self.in_out = in_out #区分输入输出
        self.elements_per_ringbuffer = chunks #用于限制deque长度
        self.frames_per_element = chunksize#每次读取的字节流大小
        self.samples_per_frame = channels
        self.bytes_per_sample = 2  # int16
        self.name = name
        self.channels = channels
        self._ringbuffer = collections.deque(
            [b"0" * self.bytes_per_sample * channels * chunksize] * chunks,
            maxlen=self.elements_per_ringbuffer)
        # print(self._ringbuffer)

        self.p = pyaudio.PyAudio()  # pylint: disable=invalid-name
        self.default_output = self.p.get_default_output_device_info()  # 获取默认音频输出设备信息
        self.default_input = self.p.get_default_input_device_info()  # 获取默认音频输入设备信息
        self.outputdeviceindex = self.default_output['index']  # 获取默认音频输出设备index
        self.inputdeviceindex = self.default_input['index']  # 获取默认音频输出设备index
        # print('default output device index: %s' %self.outputdeviceindex)
        # print('default input device index: %s' %self.inputdeviceindex)
        if rate == "auto":
            self.rate = self.default_output['defaultSampleRate']
        else:
            self.rate = rate
        self.has_new_audio = False

    def start(self):
        """开始记录 """
        if self.in_out == 'in':

            # index = self.inputdeviceindex
            channles = self.p.get_device_info_by_index(self.inputdeviceindex)['maxInputChannels']
            print(self.inputdeviceindex,channles,self.rate)
            stream = self.p.open(
                format=pyaudio.paInt16,
                # channels=self.channels,
                channels=channles,
                # rate=int(self.rate),
                rate=44100,
                input=True,
                frames_per_buffer=self.frames_per_element,
                input_device_index=self.inputdeviceindex,
                # as_loopback=False
            )
        elif self.in_out =='out':
            # index = self.outputdeviceindex
            channles = self.p.get_device_info_by_index(self.outputdeviceindex)['maxOutputChannels']
            stream = self.p.open(
                format=pyaudio.paInt16,
                # channels=self.channels,
                channels=channles,
                rate=int(self.rate),
                input=True,
                frames_per_buffer=self.frames_per_element,
                input_device_index=self.outputdeviceindex,
                # input_device_index=int(self.deviceindex),
                as_loopback=True
            )

        def record():
            """
            连续读取数据并将其添加到缓冲区
            """
            while True:
                audio_string = stream.read(self.frames_per_element)
                self._ringbuffer.append(audio_string)
                self.has_new_audio = True #继续循环

        thread = threading.Thread(target=record)
        thread.start()

    @property
    def ringbuffer(self):
        """

        :return:返回 deque对象
        """
        self.has_new_audio = False#停止循环
        return self._ringbuffer
