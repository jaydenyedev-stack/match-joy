# 网页版公网部署（GitHub Pages）

## 1. 生成部署文件
```bash
bash deploy_github_pages.sh
```

会自动构建网页并生成 `docs/` 目录。

---

## 2. 提交并推送到 GitHub
```bash
git add docs
git commit -m "deploy web build"
git push
```

---

## 3. 打开 GitHub Pages
在仓库 Settings → Pages：
- Source 选择 `main` 分支
- Folder 选择 `/docs`

保存后会得到一个公网地址：
```
https://<你的用户名>.github.io/<仓库名>/
```

手机直接打开这个地址即可访问。
