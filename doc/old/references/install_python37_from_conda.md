以Linux系统为例

# 下载MiniConda安装脚本

下载地址：https://docs.conda.io/en/latest/miniconda.html ，选择 Python 3.7 -	Miniconda3 Linux 64-bit

下载脚本：

`wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.11.0-Linux-x86_64.sh`

安装：

```shell
bash ./Miniconda3-py37_4.11.0-Linux-x86_64.sh

source ~/.bashrc 

# 创建本项目要用到的python3.7.12环境
conda create -n python37 python3.7.12

# 切换python版本到3.7.12
conda activate python37

# 检查python3.7.12是否安装成功
python3 --version
```
