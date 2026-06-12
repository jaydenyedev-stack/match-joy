# 网页版运行指南（pygbag）

## 1. 构建网页版
```bash
bash build_web.sh
```

构建输出在 `build/web`。
脚本会生成 `match-3.gameplay.html`，`index.html` 会自动跳转到它。
如果浏览器仍是黑屏，请先清理旧缓存与输出，再重新构建。

---

## 2. 本机启动网页服务
```bash
bash run_web.sh
```
端口被占用时可以改成：
```bash
PORT=8888 bash run_web.sh
```

浏览器访问：
```
http://localhost:8000
```
如果看到的是目录列表，说明服务启动目录不对，请确保运行的是脚本 `run_web.sh`，或直接访问：
```
http://localhost:8000/index.html
```
如果黑屏，建议在浏览器里强制刷新并清理站点数据后再打开。

---

## 3. 手机上打开
保证电脑和手机在同一 Wi-Fi 下，找出电脑的局域网 IP（如 192.168.1.20），然后在手机浏览器打开：
```
http://你的电脑IP:8000
```
如果看到的是目录列表，可以改为：
```
http://你的电脑IP:8000/index.html
```
