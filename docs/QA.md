# 常见问题与答案

我们编译原理助教众多，希望同学们踊跃提问。同时我们会挑选一些比较有代表性或者提问次数较多的问题放到这里供同学们查阅。

## 环境配置

1.WSL环境下使用 `systemctl`指令报错：`System has not been booted with systemd as init system (PID 1). Can’t operate.`

由于部分WSL使用 `SysV init`而非 `systemd`管理服务，解决方法是使用 `service`指令代替 `systemctl`指令。

2.如何更新代码仓库: 请在终端依次输入以下指令

（注意：你的终端所在目录应在实验代码文件夹根目录下，如果你不确定，请新建终端）

```bash
git stash	# 将当前未提交的修改暂时储藏
git pull	# 从远程仓库拉取新的实验代码
git stash pop	# 恢复先前暂时储藏的修改
```
