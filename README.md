# SYsU-lang **(2.0)**

中山大学（**S**un **Y**at-**s**en **U**niversity）[编译原理](https://arcsysu.github.io/teach/dcs290/s2024.html)课程实验 **2.0** 版。

根据此前的教学反馈，我们对原先实验框架进行了彻底的重构，重构后的版本：

- 与 CMake 构建系统和 VSCode 编辑器深度结合，提供了涵盖构建、调试、评测、打包的完整解决方案，为同学们带来了现代化的开发体验；
- 预置了完整、规范、采用最佳实践的基础示例代码和项目组织结构，大大降低了同学们的上手难度，减少了与课程内容无关的工程量；
- 设计了自定义配置机制，允许同学们根据自身情况和偏好选择完成实验的方式，提高了实验的灵活性；
- 精简了评测样例，改进了评分脚本，可以提供更加清晰的评测结果，帮助同学们更好地理解实验要求和自己代码的问题；
- 提供了环境配置脚本以及开箱即用的标准化开发容器，简化了环境配置，大大降低了环境差异引发问题的可能性；
- 根据示例代码重新撰写的“手把手”实验文档言之有物，从而提供了更加具体和清晰的实验指导。

> 由于时间有限，重构仍然在进行中，实验框架仍在积极更新…………

# 内容

本实验共由 5 个任务组成：

- [任务 0：环境准备](task/0)
- [任务 1：词法分析](task/1)
- [任务 2：语法分析](task/2)
- [任务 3：中间代码生成](task/3)
- [任务 4：中间代码优化](task/4)

> 到任务各自的目录中查看具体的任务要求。

# 准备

## 安装

我们提供了开箱即用的标准化开发容器，[这篇文章](https://zwshan.github.io/SYsU-lang-doc/#/introduction/environment)介绍了如何在你的电脑上拉取并使用它。如果同学们可以使用 GitHub Codespaces，一种简单且快速的体验方式是直接点击仓库右上角的 `Code` 来一键式地创建 Codespace，只需经过一段时间的等待就可以直接使用。

如果你不想使用容器而是想直接在自己的 Linux 环境中使用本框架，请使用以下 bash 命令：

```bash
# 安装依赖（以 Ubuntu 22.04 为例）
sudo apt-get update
sudo apt-get install -y build-essential git cmake ninja-build default-jdk \
  python3 bison flex
# 克隆仓库
git clone https://github.com/arcsysu/SYsU-lang2.git -b master --single-branch --depth 1
# 进入仓库
cd SYsU-lang
# 安装 antlr 与 llvm
cd antlr && bash install.sh
cd ../llvm && bash install.sh
```

然后，使用 VSCode 的 Remote - SSH 插件连接到你的 Linux 环境，打开仓库文件夹，即可开始实验。

实验所需的 VSCode 插件已经全部列在 [`.vscode/extensions.json`](.vscode/extensions.json) 中，在打开文件夹时，VSCode 会自动提示你安装这些插件，你只需点击提示进行安装即可。

## 配置

注意仓库根目录下的 `config.cmake` 文件，这是一个自定义配置文件，你可以根据自己的情况和偏好修改它。至少，你需要在其中填入你的姓名和学号。

通过这个文件，你可以选择实验一和实验二的完成方式：是使用 bison+flex 还是 antlr，相应地，你的程序也会在我们评测时使用相应的方式运行。

除此之外，你还可以通过它配置第一个之后的每个实验是否“复活”。所谓“复活”，是指将程序的输入由源代码的内容改为前一个实验的标准答案。由于本实验是线性、渐进的，如果你在前一个实验中“挂了”或是做得不够好，那么就可以选择“复活”来同步进度，从而继续后面的实验。

> 复活机制默认关闭，启用复活需要让预置的示例代码适配变化后的输入，我们会尽快在将来的更新中给出适配代码。

# 开始

现在，你已经准备好了，请按照每个任务的具体要求，开始你的编译器实验之旅吧！

你可以在这里找到更多的参考文档：[https://zwshan.github.io/SYsU-lang-doc](https://zwshan.github.io/SYsU-lang-doc)。
