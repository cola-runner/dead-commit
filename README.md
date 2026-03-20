```
 ██████╗ ███████╗ █████╗ ██████╗
 ██╔══██╗██╔════╝██╔══██╗██╔══██╗
 ██║  ██║█████╗  ███████║██║  ██║
 ██║  ██║██╔══╝  ██╔══██║██║  ██║
 ██████╔╝███████╗██║  ██║██████╔╝
 ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝
  ██████╗ ██████╗ ███╗   ███╗███╗   ███╗██╗████████╗
 ██╔════╝██╔═══██╗████╗ ████║████╗ ████║██║╚══██╔══╝
 ██║     ██║   ██║██╔████╔██║██╔████╔██║██║   ██║
 ██║     ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██║   ██║
 ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║██║   ██║
  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝   ╚═╝
```

**A terminal-based mystery game. You are a programmer. You use real Linux commands. The production server is on fire. But this is not a normal incident.**

[English](#english) | [中文](#中文)

---

## English

### What is this?

3 AM. PagerDuty wakes you up. The production database is melting — 847 connections against a pool of 100. You `ssh` into the bastion host, `grep` through the logs, and find something that shouldn't be there.

A service is exporting 2.34 million users' real-time location data to an external IP. Your missing colleague left hidden messages inside a code review. And the clock is ticking.

You play by typing real commands: `ls`, `cat`, `grep`, `ssh`, `decrypt`, `kill`. No fake GUI. No hand-holding. Just you, a terminal, and a conspiracy that goes deeper than a supply chain attack.

### Install & Play

```bash
pip install git+https://github.com/cola-runner/dead-commit.git
dead-commit
```

Or clone and run locally:

```bash
git clone https://github.com/cola-runner/dead-commit.git
cd dead-commit
pip install .
dead-commit
```

Requires Python 3.10+ and a terminal that supports 256 colors.

### How to Play

Type commands like you would in a real terminal:

| Command | What it does |
|---------|-------------|
| `ls` | List items in the current scene |
| `cat <file>` | Read a file or examine an object |
| `grep <keyword>` | Search for patterns in logs |
| `ssh <host>` | Connect to a remote machine |
| `take <item>` | Pick up an item |
| `use <item>` | Use an item from your inventory |
| `decrypt <file>` | Decrypt an encrypted file |
| `help` | Show available commands |

No walkthrough needed. Read everything. Think like an engineer.

### Features

- Real Linux command interface — no point-and-click, no menus
- Pixel art scenes rendered in your terminal
- Bilingual: full Chinese and English support
- Auto-save on every scene transition
- A story that will make you mass-audit your `node_modules`

### Tech Stack

Python, [Textual](https://github.com/Textualize/textual), [Rich](https://github.com/Textualize/rich), [rich-pixels](https://github.com/darrenburns/rich-pixels), Pillow

### Status

- Chapter 1: Playable
- Chapter 2: Playable
- Chapter 3: Coming

### License

MIT

---

## 中文

### 这是什么？

凌晨三点，PagerDuty 把你震醒。生产数据库在炸——连接池 100 个上限，活跃连接 847 个。你 `ssh` 进跳板机，`grep` 日志，发现了不该出现的东西。

一个服务正在把 234 万用户的实时位置数据导出到境外 IP。你失联的同事在代码审查里藏了求救信号。倒计时已经开始。

你用真实的命令来玩：`ls`、`cat`、`grep`、`ssh`、`decrypt`、`kill`。没有假 GUI，没有新手引导。只有你、一个终端、和一个比供应链攻击更深的阴谋。

### 安装 & 运行

```bash
git clone https://github.com/cola-runner/dead-commit.git
cd dead-commit
pip install -r requirements.txt
python main.py
```

需要 Python 3.10+ 和支持 256 色的终端。

### 怎么玩

像在真实终端里一样输入命令：

| 命令 | 作用 |
|------|------|
| `ls` | 查看当前场景的物品 |
| `cat <文件>` | 阅读文件或检查物品 |
| `grep <关键词>` | 在日志中搜索关键信息 |
| `ssh <地址>` | 连接到远程服务器 |
| `take <物品>` | 拾取物品 |
| `use <物品>` | 使用背包中的道具 |
| `decrypt <文件>` | 解密加密文件 |
| `help` | 显示可用命令 |

不需要攻略。仔细阅读每一条信息。像工程师一样思考。

### 特性

- 真实 Linux 命令交互——没有点击，没有菜单
- 终端内渲染的像素风场景画面
- 中英双语完整支持
- 每次场景切换自动存档
- 一个会让你回去审计 `node_modules` 的故事

### 技术栈

Python, [Textual](https://github.com/Textualize/textual), [Rich](https://github.com/Textualize/rich), [rich-pixels](https://github.com/darrenburns/rich-pixels), Pillow

### 进度

- 第一章：可玩
- 第二章：可玩
- 第三章：开发中

### 协议

MIT
