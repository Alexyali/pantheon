# Test CLDCC in Pantheon

该分支（cellular_test）将实现了CLDCC(Configurable Low Delay Congestion Control)算法的UDT仓库加入了pantheon子仓库模块。并且修改了`src/analysis`部分python代码，将原本的95%单向延迟指标替换为了平均单向延迟。

## 编译

参考pantheon的README。

### 子模块

下载更新子模块。

```shell
$ git submodule update --init --recursive
# or tools/fetch_submodules.sh
```

注意：因为webrtc和quic的代码库过大，因此本分支取消了这两个模块。如果还想下载可以根据`.gitmodules`找到地址。

### 安装依赖

分别为pantheon和各种拥塞控制算法安装依赖。

```shell
# patheon dependencies
$ tools/install_deps.sh

# congestion control schemes dependencies
$ src/experiments/setup.py --install-deps (--all | --schemes "<cc1> <cc2> ...")
```

### 启动

编译各个拥塞控制仓库以及为其准备运行环境。

```shell
$ sudo sysctl -w net.ipv4.ip_forward=1
$ src/experiments/setup.py [--setup] [--all | --schemes "<cc1> <cc2> ..."]
```

注意：每次重启系统都必须运行该启动指令。

## 本地仿真网络运行

pantheon基于mahimahi实现本地网络仿真，mahimahi用到的网络路径见`traces/`，分别包括不同的无线网络场景。

```shell
$ src/experiments/test.py local (--all | --schemes "<cc1> <cc2> ...")
```

运行`src/experiments/test.py local -h`查看详细说明。

- `--data-dir [DIR]` 运行结果保存的文件夹

- `--uplink-trace [trace path]` 设置mahimahi的上行链路的路径地址

- `--downlink-trace [trace path]` 设置mahimahi的下行链路的路径地址

- `--run-times [number]` 每个算法的运行次数

- `--random-order` 随机顺序运行算法

- `-t [sec]` 每个算法的运行时长

## 数据分析

pantheon自动分析运行算法生成的日志，并生成包含结果图表的PDF，保存在DIR中。PDF报告见`pantheon_report.pdf`。

```shell
src/analysis/analyze.py --data-dir DIR
```

## 简化版脚本

`exper.sh`是在LTE仿真网络下测试pantheon的脚本，直接执行可以运行程序并分析生成结果。该脚本仅选择了cubic、bbr、vegas和cldcc算法，因此在**编译**部分涉及`--schemes`的可以直接指定`--schemes "cubic vegas bbr cldcc"`。

注意：运行该脚本前需要先完成**编译**部分的所有内容。

```shell
$ mkdir result
$ sh exper.sh
```

运行生成的结果分析PDF文件在`result/PDF`中。