# 智慧厨房数据看板 - 免费部署指南

本系统已配置好，可以直接部署到以下免费平台。请根据您的需求选择一种方式。

---

## 方案一：Render（推荐，操作最简单）

**特点**：
- ✅ 永久免费
- ✅ 自动化部署（连接 GitHub 后，每次推送代码自动更新）
- ⚠️ 限制：免费实例在 15 分钟无访问后会休眠，下次访问需要等待约 50 秒启动。

**部署步骤**：
1. **上传代码到 GitHub**
   - 注册并登录 [GitHub](https://github.com/)。
   - 创建一个新的仓库（Repository）。
   - 将本项目代码推送到该仓库。

2. **在 Render 创建服务**
   - 访问 [Render.com](https://render.com/) 并注册/登录。
   - 点击右上角 **New +** -> 选择 **Web Service**。
   - 连接您的 GitHub 账号并选择刚才创建的仓库。

3. **配置服务**（Render 会自动检测，只需确认以下几项）：
   - **Name**: 起个名字，例如 `kitchen-dashboard`。
   - **🔴 Root Directory**: **必须填写 `dashboard`** (非常重要！否则会报错找不到文件)。
   - **Runtime**: 选择 **Python 3**。
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: 选择 **Free**（免费版）。

4. **完成**
   - 点击 **Create Web Service**。
   - 等待几分钟构建完成，您会获得一个 `https://xxxx.onrender.com` 的网址。
   - **直接把这个网址发给别人即可访问！**

---

## 方案二：PythonAnywhere（稳定，无休眠）

**特点**：
- ✅ 永久免费
- ✅ 不会休眠（访问速度快）
- ⚠️ 限制：需要手动上传代码或使用 git拉取；每 3 个月需要登录后台点一下“续期”按钮。

**部署步骤**：
1. **注册账号**
   - 访问 [PythonAnywhere](https://www.pythonanywhere.com/)，注册一个 **Beginner**（免费）账号。

2. **上传代码**
   - 登录后点击 **Files** 选项卡。
   - 可以直接上传 `dashboard` 文件夹中的文件，或者在 **Consoles** -> **Bash** 中使用 `git clone` 拉取您的 GitHub 仓库。

3. **配置 Web 应用**
   - 点击 **Web** 选项卡 -> **Add a new web app**。
   - 点击 **Next** -> 选择 **Flask** -> 选择 **Python 3.10**（或您喜欢的版本）。
   - **Path**: 修改为您上传代码的路径（例如 `/home/您的用户名/dashboard/app.py`）。

4. **安装依赖**
   - 打开 **Consoles** -> **Bash**。
   - 运行：`pip3 install --user flask pandas openpyxl gunicorn`

5. **完成**
   - 回到 **Web** 选项卡，点击 **Reload** 按钮。
   - 点击顶部的链接（例如 `您的用户名.pythonanywhere.com`）即可访问。

---

## 常见问题

**Q: 为什么 Render 打开很慢？**
A: 免费版在一段时间没有人访问后会自动休眠以节省资源。下次访问时需要重新启动，大约需要 50 秒。启动后速度就正常了。

**Q: 数据更新了怎么办？**
A: 
- **Render**: 直接将新的 Excel 文件提交到 GitHub，Render 会自动检测到变化并重新部署。
- **PythonAnywhere**: 需要手动上传新的 Excel 文件覆盖旧文件，然后在 Web 选项卡点击 Reload。
