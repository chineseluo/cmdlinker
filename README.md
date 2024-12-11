# **CmdLinker**

# [![pyversions](https://img.shields.io/badge/CmdLinker-v0.1.x-green)](https://pypi.org/project/cmdlinker/)

`CmdLinker`将为您提供简单、可操作的命令对象的调用方式，通过链式调用去使用各种命令，获取请求/响应，不在局限于将简单的命令字符串交给各种ssh工具包，修改执行命令时，不在需要进行各种繁琐的字符串的替换之类的操作或直接重新编写命令

## **适用系统/中间件**

- 所有可在linux/windows下运行的命令
- 自研云原生中间件的可执行命令
- 开源组件的命令，docker/redis/mysql/tidb/......

## **常规使用场景**

- 云原生中间件cli命令的回归
- 混沌测试
- 运维部署脚本
- python版的shell脚本
- ......

## **设计思想**

- 将yaml文件编译成可执行的命令对象:cmd_obj
- 提供链式调用的方式给操作者，set/get
- 告别繁琐的操作命令字符串的方式，使命令更具有逻辑性
- 拥抱开源

## **主要特点**

- 通过指定mode模式（SSH，SHELL），将命令对象yaml文件转换为对应模式下的py模块
- 提供了命令对象set/get方法，去设置/获取对应命令的参数
- 提供了内置的checker，可检查命令对象是否符合规范
- 提供了内置的runner方法，去获取本地/远程命令执行的请求/响应
- 简化了SSH/SHELL命令的执行操作操作，通过实例化命令对象，调用runner即可获取请求响应

## **其他**

`cmdlinker`内置了两种模式，SSH/SHELL，用于生成不同场景下的命令对象

- SSH模式，主要用于执行远程链接的命令，举例：你需要链接到某台服务器，执行命令A，获取A命令的返回结果，可在yaml中配置SSH模式
- SHELL模式，主要用于本地执行的命令，不需要链接服务器端口，不需要权限认证相关的账号密码，举例：在linux环境执行`ls -l`，只需要指定SHELL模式即可

# **使用方法** #

安装cmdlinker
~~~
pip3 install cmdlinker
~~~

验证安装是否成功

~~~
cmdlinker -v
~~~
出现版本信息，表示你得环境已经支持`cmdlinker`相关命令
~~~
PS C:\Users\Dell> cmdlinker -v

  ____               _ _     _       _
 / ___|_ __ ___   __| | |   (_)_ __ | | _____ _ __
| |   | '_ ` _ \ / _` | |   | | '_ \| |/ / _ \ '__|
| |___| | | | | | (_| | |___| | | | |   <  __/ |
 \____|_| |_| |_|\__,_|_____|_|_| |_|_|\_\___|_|


The cmdlinker version is 0.1.1
repository：https://github.com/chineseluo/cmdlinker
authors：成都-阿木木<848257135@qq.com>
community（QQ群）：816489363
~~~


简单例子：使用linux的free -b -t 举例

第一步编写命令yaml
~~~yaml
entry: "free" # 主命令
mode: "SSH"
parameters:
  - mapping_name: "b" # 映射命令
    original_cmd: "-b" # 映射命令
    value: False # 是否需要值
    mutex: False # 是否互斥
    default: None # 命令默认值
  - mapping_name: "t" # 映射命令
    original_cmd: "-t" # 原命令
    value: False # 命令是否需要值
    mutex: False # 命令之间是否互斥
    default: None # 命令默认值
~~~

第二步，生成yaml
- 通过命令生成
- 通过导入`cmdlinker`生成

通过命令生成

~~~
 cmdlinker init -f .\Ost.yaml
~~~

通过导入`cmdlinker`生成
~~~
from cmdlinker.analyse import generator
generator("../example/free.yaml")
~~~

生成的python对象见example模块下的free.py/Free.yaml文件，会生成两个命令类，入口entry类为Free，子命令类B，子命令T

`cmdlinker`提供了两种设置命令的方式，运行于不同的场景
- 保持模式HOLD
- 传递模式TRANSMIT

**保持模式HOLD**
~~~
free = Free(host="192.168.1.5", name="root", pwd="123456", port="22")
free.hset_b().hset_t().runner()
~~~
HOLD模式进行hset操作，会返回Free对象本身，可以继续操作Free下的子命令对象

**传递模式TRANSMIT**
~~~
free = Free(host="192.168.1.5", name="root", pwd="123456", port="22")
free.tset_b().pre.tset_t().runner()
~~~

~~~
free = Free(host="192.168.1.5", name="root", pwd="123456", port="22")
free.tset_b().root.tset_t().runner()
~~~
TRANSMIT模式进行tset操作，会进入子命令对象本身，Free().tset_t()此时会返回T对象，可以通过pre定位到他的父级命令，或者通过root定位到根命令Free下进行操作

---

`cmdlinker`提供了查询设置的命令参数的方法

~~~
free = Free(host="192.168.1.5", name="root", pwd="123456", port="22")
free.tset_b().pre.tset_t().runner()
# 查询
b = free.b() #返回B命令对象
b.value # 返回b对象的值
~~~


`cmdlinker`提供了查询运行命令的方法
~~~
free = Free(host="192.168.1.5", name="root", pwd="123456", port="22")
free.tset_b().pre.tset_t().runner()
free.exec_cmd()
~~~
exec_cmd()返回执行命令的字符串

`cmdlinker`提供了查询运行命令对象的方法
~~~
free = Free(host="192.168.1.5", name="root", pwd="123456", port="22")
free.tset_b().pre.tset_t().runner()
free.collector()
~~~
collector()返回一个命令对象列表

`cmdlinker`提供了运行命令对象的方法
~~~
free = Free(host="192.168.1.5", name="root", pwd="123456", port="22")
free.tset_b().pre.tset_t().runner()
~~~
通过runner()可以执行命令对象的方法，必须从主命令开始，也就是entry命令实例化命令对象，传递子参数，然后调用runner()


## **OpenSourceTest cmdlinker 社区**

欢迎小伙伴加群，讨论cmdlinker相关问题，或提出优化建议！

**QQ群（自动化测试-夜行者）：816489363**