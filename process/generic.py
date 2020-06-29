# -*- coding: utf-8 -*-
# @Author  : lucius
# @Email   : cnotperfect@foxmail.com

"""与音频处理相关的通用功能。"""

import audioop
import logging
import re
import numpy as np

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def rms(audio_fragment, sample_width_in_bytes=2):
    """Given audio fragment, return the root mean square.
    给定音频片段，返回均方根。"""
    # Equal to
    # return int(np.sqrt(np.mean(np.square(
    #     np.absolute(audio_fragment.astype(np.float))))))
    return audioop.rms(np.abs(audio_fragment), sample_width_in_bytes)


def notespace(spn_start, spn_end, step=1.0, start_offset=0.0, end_offset=0.0):
    """
    Given note endpoints in scientific pitch notation, return frequencies
    spaced evenly on a log scale.
    给定的音符端点在科学音高表示法，返回频率在对数尺度上平均间隔。
    """
    # pylint: disable=invalid-name

    def n(spn):
        """
        Given note in scientific pitch notation, return semitone distance from
        A4.
        在科学的音高表示法中，返回半音距离A4。
        """
        m = re.match(r"([A-G]+#*)(-*\d+)", spn)
        name = m.group(1)
        octave = int(m.group(2))
        note_names = [
            "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
            ]
        return note_names.index(name)-9 + (octave-4)*12

    def f(n):
        """
        Given semitone distance from A4 and assuming A440 pitch standard,
        return frequency in hertz.
        考虑到A4的半音距离和A440的音高标准，返回频率，单位为赫兹。
        """
        return 2.0**(n/12.0) * 440.0

    n_start = int(n(spn_start) + start_offset)
    n_end = int(n(spn_end) + end_offset)
    sample_count = int(abs(n_end - n_start)/step + 1)
    # print(n_start, n_end, sample_count,1111)
    logger.debug(
        "notespace - f(n_start): {}, f(n_end): {}, sample_count: {}".format(
            f(n_start), f(n_end), sample_count))

    return [f(n) for n in np.linspace(n_start, n_end, sample_count)]


def a_weight(x_coordinates):
    """Return A-weighting fitted to the given frequency dimension.
    返回加权符合给定的频率维数。
    """
    a_weight_frequency = [
        10, 12.5, 16, 20, 25, 31.5, 40, 50,
        63, 80, 100, 125, 160, 200, 250, 315,
        400, 500, 630, 800, 1000, 1250, 1600, 2000,
        2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500,
        16000, 20000
        ]
    a_weight_decibels = [
        -70.4, -63.4, -56.7, -50.5, -44.7, -39.4, -34.6, -30.2,
        -26.2, -22.5, -19.1, -16.1, -13.4, -10.9, -8.6, -6.6,
        -4.8, -3.2, -1.9, -0.8, 0.0, 0.6, 1.0, 1.2,
        1.3, 1.2, 1.0, 0.5, -0.1, -1.1, -2.5, -4.3,
        -6.6, -9.3
        ]
    return np.interp(x_coordinates, a_weight_frequency, a_weight_decibels)
