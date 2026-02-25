# 智慧厨房数据看板 - 免费部署指南

本指南将教你如何将项目部署到云端，生成一个可以发给别人访问的网址。
推荐使用 **PythonAnywhere**（最简单、稳定，适合新手）或 **Render**。

---

## 方案一：使用 PythonAnywhere 部署（推荐 ✨）

**优点**：配置极其简单，Python 环境预装好，基本不会报错。
**缺点**：免费版域名是 `你的用户名.pythonanywhere.com`。

### 1. 注册账号
访问 [www.pythonanywhere.com](https://www.pythonanywhere.com/)，点击 **Sign up**，选择 **Create a Beginner account**（免费版）。

### 2. 上传代码
登录后，点击右上角的 **Consoles** -> **Bash**。在黑底白字的命令行窗口中输入以下命令（复制粘贴并回车）：

```bash
# 1. 克隆代码
git clone https://github.com/phyllisllc/shujukanban.git

# 2. 进入项目目录
cd shujukanban/dashboard

# 3. 安装依赖 (可能需要一点时间)
pip install -r requirements.txt
```

### 3. 配置 Web 应用
1. 点击页面右上角的 **Web** 标签页。
2. 点击 **Add a new web app** 按钮。
3. 点击 **Next**。
4. 选择 **Flask**。
5. 选择 **Python 3.10**（或者 3.9，都行）。
6. **Path**：直接点击 Next（默认即可，稍后我们再改）。
7. 创建完成后，你会在页面上看到 **Code** 部分。

### 4. 修改关键配置（最重要的一步！）
在 **Web** 标签页中，找到 **Code** 部分：

*   **Source code**: 点击编辑图标（铅笔），填入：
    `/home/你的用户名/shujukanban/dashboard`
    *(注意：把“你的用户名”换成你注册时的名字，比如 `/home/zhangsan/shujukanban/dashboard`)*

*   **Working directory**: 同样点击编辑，填入：
    `/home/你的用户名/shujukanban/dashboard`

*   **WSGI configuration file**: 点击那个长长的文件链接（例如 `/var/www/zhangsan_pythonanywhere_com_wsgi.py`）。
    编辑器打开后，**删除所有内容**，然后粘贴以下代码：

    ```python
    import sys
    import os

    # 指向你的项目目录
    path = '/home/你的用户名/shujukanban/dashboard'
    if path not in sys.path:
        sys.path.append(path)

    # 导入 Flask 应用
    from app import app as application
    ```
    *(再次提醒：把代码里的“你的用户名”换成你真实的用户名！)*
    点击右上角的 **Save** 保存，然后点击面包屑导航回到 **Web** 页面。

### 5. 启动网站
在 **Web** 页面顶部，点击绿色的 **Reload <你的网址>** 按钮。
点击你的网址（例如 `zhangsan.pythonanywhere.com`），应该就能看到数据看板了！

---

## 方案二：使用 Render 部署

1.  注册 [Render](https://render.com/)。
2.  点击 **New +** -> **Web Service**。
3.  连接你的 GitHub 仓库。
4.  配置如下：
    *   **Name**: `kitchen-dashboard`
    *   **Root Directory**: `dashboard` (**必须填！**)
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app`
5.  点击 **Create Web Service**。

---

## 常见问题

**Q: PythonAnywhere 部署后报错 "Something went wrong"?**
A: 去 **Web** 页面，找到 **Log files**，查看 **Error log**。通常是因为 WSGI 文件里的路径写错了（用户名没改对），或者依赖包没安装好。

**Q: 数据不对或图表不显示？**
A: 确保你之前上传代码时，Excel 文件也在 `dashboard/data` 目录下。我们的代码已经包含了 Excel 文件，只要 Git 克隆下来就有。
