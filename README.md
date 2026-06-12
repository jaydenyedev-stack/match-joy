# Match Joy

Match Joy is a simple match-3 puzzle game built with Python and Pygame. It demonstrates the core gameplay loop of a casual tile-matching game: swapping adjacent blocks, detecting matches, clearing tiles, dropping remaining blocks, filling new blocks, scoring, and ending the game when moves run out.

The project also includes scripts for building and running a web version with pygbag, so the game can be played in a browser or deployed with GitHub Pages.

## Features

- 8x8 match-3 game board
- Click two adjacent blocks to swap them
- Automatic match detection for rows and columns
- Tile clearing, falling, and refill logic
- Score counter
- Limited moves system
- Pop, spawn, cascade, and screen shake effects
- Desktop version powered by Pygame
- Browser build support through pygbag

## Project Structure

```text
.
├── main.py                  # Game entry point
├── test.py                  # Main game logic
├── images/                  # Tile image assets
├── build_web.sh             # Build the browser version
├── run_web.sh               # Run the built browser version locally
├── deploy_github_pages.sh   # Prepare files for GitHub Pages
├── WEB_BUILD.md             # Web build guide
└── WEB_DEPLOY.md            # GitHub Pages deployment guide
```

## Run Locally

Install Pygame first:

```bash
pip install pygame
```

Then start the desktop game:

```bash
python main.py
```

If your system uses `python3` instead of `python`, run:

```bash
python3 main.py
```

## Run Web Version

Build the web version:

```bash
bash build_web.sh
```

Start a local web server:

```bash
bash run_web.sh
```

Open the game in your browser:

```text
http://localhost:8000/index.html
```

If port `8000` is already in use, choose another port:

```bash
PORT=8888 bash run_web.sh
```

## Deploy to GitHub Pages

Generate the deployment files:

```bash
bash deploy_github_pages.sh
```

Then commit and push the generated `docs/` directory:

```bash
git add docs
git commit -m "deploy web build"
git push
```

In the GitHub repository settings, enable GitHub Pages with:

- Source: `main`
- Folder: `/docs`

## Notes

This is a learning/demo project focused on the basic mechanics of a match-3 game. It is not intended to be a full commercial game, but it is a good starting point for experimenting with puzzle game logic, animations, scoring rules, and browser deployment.

---

# 中文说明

Match Joy 是一个使用 Python 和 Pygame 开发的简易三消益智游戏。它实现了休闲三消游戏的核心玩法：交换相邻方块、检测匹配、消除方块、方块下落、补充新方块、计分，以及步数用完后的游戏结束流程。

项目中也包含了使用 pygbag 构建网页版的脚本，因此游戏既可以作为桌面程序运行，也可以打包成网页版本，在浏览器中游玩或部署到 GitHub Pages。

## 功能特点

- 8x8 三消棋盘
- 点击两个相邻方块进行交换
- 自动检测横向和纵向匹配
- 方块消除、下落和自动补充
- 分数统计
- 步数限制
- 消除、生成、连锁和屏幕抖动动画效果
- 基于 Pygame 的桌面版本
- 支持通过 pygbag 构建浏览器版本

## 项目结构

```text
.
├── main.py                  # 游戏入口文件
├── test.py                  # 主要游戏逻辑
├── images/                  # 方块图片资源
├── build_web.sh             # 构建网页版
├── run_web.sh               # 本地运行网页版
├── deploy_github_pages.sh   # 生成 GitHub Pages 部署文件
├── WEB_BUILD.md             # 网页版构建说明
└── WEB_DEPLOY.md            # GitHub Pages 部署说明
```

## 本地运行

先安装 Pygame：

```bash
pip install pygame
```

然后启动桌面版游戏：

```bash
python main.py
```

如果你的系统使用的是 `python3` 命令，可以运行：

```bash
python3 main.py
```

## 运行网页版

先构建网页版：

```bash
bash build_web.sh
```

启动本地网页服务：

```bash
bash run_web.sh
```

然后在浏览器打开：

```text
http://localhost:8000/index.html
```

如果 `8000` 端口已被占用，可以换一个端口：

```bash
PORT=8888 bash run_web.sh
```

## 部署到 GitHub Pages

生成部署文件：

```bash
bash deploy_github_pages.sh
```

然后提交并推送生成的 `docs/` 目录：

```bash
git add docs
git commit -m "deploy web build"
git push
```

在 GitHub 仓库设置中启用 GitHub Pages：

- Source 选择 `main`
- Folder 选择 `/docs`

## 说明

这是一个用于学习和演示的三消游戏项目，重点是展示三消游戏的基础逻辑和实现方式。它不是完整的商业游戏，但很适合作为练习游戏逻辑、动画效果、计分规则和网页部署的起点。
