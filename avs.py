# -*- coding: utf-8 -*-
# @Author  : lucius
# @Email   : cnotperfect@foxmail.com

"""跨平台音频输入输出监控"""

# pylint: disable=wrong-import-position, ungrouped-imports
from __future__ import division
import pyaudio
import sys
# from output.vsipy_in_qt import *

sys.dont_write_bytecode = True  # noqa
from warnings import simplefilter
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from output.vsipy_in_qt import qt
simplefilter(action='ignore', category=FutureWarning)
import logging
import os
import signal
import output.vispyqt
from auxiliary import conf, utils
from process.audio_processor import AudioProcessor

if os.name == "nt":  # nt为windwos
    from input.portaudio import Portrecorder as Recorder
    from auxiliary import windows
else:
    from input.pulseaudio import Pulserecorder as Recorder
    from auxiliary import gnu

TITLE = "AudioMonitor-by-luciuis"  # 用于创建配置文件夹


def main():
    """
    主函数

    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # 当遇到SIGINT即CTRL+C，进程采用默认default行为处理
    args = conf.parse_command_line_args()  # 定义和解析命令行参数。
    conf.setup_logging(args.loglevel)  # 根据命令行参数设置日志打印级别
    logger = logging.getLogger(__name__)  # 根据文件名初始化一个logger handle
    configs = conf.Configs(TITLE)

    recorder_in = Recorder(
        TITLE,
        chunks=configs.settings.getint('recorder', 'chunks'),
        chunksize=configs.settings.getint('recorder', 'chunksize'),
        channels=configs.settings.getint('recorder', 'channels'),
        rate=configs.settings.get('recorder', 'rate'),
        in_out='in'
    )
    recorder_out = Recorder(
        TITLE,
        chunks=configs.settings.getint('recorder', 'chunks'),
        chunksize=configs.settings.getint('recorder', 'chunksize'),
        channels=configs.settings.getint('recorder', 'channels'),
        rate=configs.settings.get('recorder', 'rate'),
        in_out='out'
    )
    audio_processor_in = AudioProcessor(
        configs,
        chunks=recorder_in.elements_per_ringbuffer,
        chunksize=recorder_in.frames_per_element,
        channels=recorder_in.channels,
        rate=recorder_in.rate,
    )
    audio_processor_out = AudioProcessor(
        configs,
        chunks=recorder_out.elements_per_ringbuffer,
        chunksize=recorder_out.frames_per_element,
        channels=recorder_out.channels,
        rate=recorder_out.rate,
    )

    # 初始化vispy窗体
    visualizer_in = output.vispyqt.Visualizer(
        TITLE,
        configs,
        audio_processor_in,
    )

    # 初始化vispy窗体
    visualizer_out = output.vispyqt.Visualizer(
        TITLE,
        configs,
        audio_processor_out,
    )

    # 放到桌面
    # pid = os.getpid()
    # logger.debug("PID: {}".format(pid))
    # # 对于windwos和linux采用不同的处理方式
    # logger.info("os.name: {}".format(os.name))
    # if os.name == "nt":
    #     win_kludges = windows.Kludges(TITLE)
    #     win_kludges.remove_taskbar_button()#隐藏窗体按钮
    #     win_timer = utils.RepeatingTimer(
    #         interval=0.1,
    #         function=win_kludges.stay_on_bottom)     #?
    #     win_timer.start()
    # else:
    #     gnu.pin_to_desktop(TITLE, pid)

    logger.info('default output device index: %s' % recorder_out.outputdeviceindex)
    logger.info('default output device info: %s' % recorder_out.default_output)
    logger.info('default input device index: %s' % recorder_in.inputdeviceindex)
    logger.info('default input device info: %s' % recorder_in.default_input)

    def update():
        """
        通过processor将数据从recorder传递给可视化工具visualizer。
        """
        # print(111111111)
        if recorder_in.has_new_audio:
            # logger.info("recorder.has_new_audio: {}".format(recorder_in.has_new_audio))
            audio_processor_in.set_audio(recorder_in.ringbuffer)
            fft_amplitudes = audio_processor_in.log_frequency_spectrum()  # fft傅里叶变换振幅
            # logger.info(fft_amplitudes)
            visualizer_in.set_data(fft_amplitudes)
        if recorder_out.has_new_audio:
            # logger.info("recorder.has_new_audio: {}".format(recorder_out.has_new_audio))
            audio_processor_out.set_audio(recorder_out.ringbuffer)
            fft_amplitudes = audio_processor_out.log_frequency_spectrum()  # fft傅里叶变换振幅
            # logger.info(fft_amplitudes)
            visualizer_out.set_data(fft_amplitudes)

    # Run
    recorder_in.start()
    recorder_out.start()
    timer = utils.RepeatingTimer(
        interval=1.0 / configs.settings.getfloat('main', 'timer_frequency'),
        function=update
    )
    '''
    t = Timer(interval, function, args=None, kwargs=None)
    interval 设置调用隔间的时间(s) 
    function 要执行的任务
    args，kwargs 传入的参数
    '''
    w = qt(visualizer_in=visualizer_in,visualizer_out=visualizer_out)
    w.show()

    timer.start()
    print('visualizer_in start')
    visualizer_in.run()
    print('visualizer_out start')
    visualizer_out.run()
    print('visualizer_in end')
    # sys.exit(app.exec_())
    # MainWindow.show()
    print('time start')




if __name__ == "__main__" and sys.flags.interactive == 0:
    main()
