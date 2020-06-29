# AV_MONITOR
一个基于python的跨平台音视频监控器

# 使用说明

```python
python avs.py -d #debug模式
```
windows下支持捕获声卡的输出信号，需要安装扩展pyaudio
使用了 <https://github.com/intxcc/pyaudio_portaudio>
这个东东扩展了pyaudio_portaudio，使pyaudio初始化流时支持as_loopback，安装时需要使用register对解释器注册。
#预览
![Image text](https://raw.githubusercontent.com/hongmaju/light7Local/master/img/productShow/20170518152848.png)



#开发初衷
音视频设备的监控

#致谢
感谢Scott W Harden大神的代码，在此基础上增加了一些功能