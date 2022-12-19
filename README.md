- TestCman.py：用于测试摄像头
- execute.py:主程序

主要是运行execute.py，其他的代码不是很确定有没有bug，没有跑过。
execute.py将检测到的图片传给后端，目前存在bug，没有写异常退出的逻辑代码。用NX跑十几分钟就会卡住。

# Jetson NX 环境配置速通

> 非常适合有一点部署经验的同学，但是个人感觉对于新生也十分友好

## SD卡烧录

随便搜一个教程，去官网上下载。

我是直接使用Arch进行镜像的烧录，一开始使用NVIDIA的SDK Manager，不知道为什么识别不到设备。

## 环境配置

烧录好之后直接设置最大功率20W 6core，然后开始升级系统：

```python
sudo apt update
sudo apt upgrade
```

去搜索安装Jtop，pip3

[(17条消息) Jetson Xavier NX 安装 jtop指导手册_GNNUXXL的博客-CSDN博客_nx安装jtop](https://blog.csdn.net/GNNUXXL/article/details/119246587)

安装东西的时候建议直接开风扇，make的时候指定线程（make -j 6）可以安装快一点。

建议先安装PySide2和Dlib，其他的比较简单。

## SSH

让Jetson NX与电脑在一个局域网内，然后直接用SSH，就可以使用电脑连接Jetson NX。

连接之后就可以使用scp传文件或者SSH连接，网络不好的时候方便传文件或者远程控制。

## PySide2

![image](https://user-images.githubusercontent.com/73021377/199190556-bc0bf953-7a06-47a4-8fc1-6947e0b04bae.png)

版本对齐很重要，踩了一堆坑之后使用这个repo的whl，两句话安好:

[chentongwilliam/PySide2-jetson-nano: PySide2 5.15.3 whl files for jetson nano (github.com)](https://github.com/chentongwilliam/PySide2-jetson-nano)

这边提一嘴，Ubantu的版本会影响Qt的版本，PySide2好像会调用系统里面的Qt动态链接库，然后不同的Ubantu版本会有影响

```
sudo apt-get install qt5-default
pip3 install PySide2-5.9.0a1-5.9.5-cp36-cp36m-linux_aarch64.whl
```

Success：

```python
from PySide2 import *
# import PySide2  不算成功
```

## Dlib

去github上搜Dlib,git clone 下来，直接:

```python
python3 setup.py install
```

## Pytorch && Torchvison

根据NVIDIA的论坛进行，上面有严格的版本对照。

由于我们的Python是3.6.9所以选好对应的版本进行

直接根据这个forums，选好对应的版本即可。

https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048

torch==1.8.0

pyside2==5.9.0

## 其他包

如果慢的话可以pip换一下源

```python
pip install -r requirement.txt
```

# 最后

以前配过Deepstream6.0,搞目标跟踪啥的，那个时候一个人搞啥都不懂，弄的死去活来的。这次部署疲劳检测，在PySide2上踩了好几天的坑，一直在走弯路，但是非常感谢学长也来帮我修Bug安包，让我学会了很多。

- 网上的教程不一定是最优最快的：比如安装某个包，有的时候一搜索都要install 源码去build，然后再改环境变量，耗时费力，还容易产生冲突。可以直接用apt 去search，有的时候能直接找到。
- 安包的时候也可以去github或者官网上找找，每个包对应的仓库一般都会有最权威的安装教程（当然也可以配合别人的教程食用）
- 还有不要乱删动态连接库。。。
- 如果能找到别人build好的wheel，建议直接pip install whell，真的可以方便非常多。就像我install PySide2一样，这玩意卡了我几天，结果两句话就能解决呜呜┭┮﹏┭┮。
- 拍视频的时候可以下载一个kzazm进行录屏。

# 引用

[原README.md](./org_README.md)
