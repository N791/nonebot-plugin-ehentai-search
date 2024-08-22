<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-ehentai-search

_✨ NoneBot ehentai search ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/N791/nonebot-plugin-ehentai-search" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ehentai-search">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-ehentai-search" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

这是一个基于NoneBot2和onebotV11的ehentai资源搜索

>[!NOTE]
>本插件需要机器人所在网络环境能够访问ehentai.org

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-ehentai-search

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-ehentai-search
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-ehentai-search
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-ehentai-search
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-ehentai-search
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_ehentai_search"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加配置项`SUPERUSERS`:

    SUPERUSERS=["机器人管理员的QQ"]

## 🎉 使用
输入ehbz_help获取帮助，搜索类型可以输入ehbz_status指令查看

> [!IMPORTANT]
>当前只支持群聊内使用

## ⭐免责声明

1.一切代码仅供研究学习，请勿用于非法用途。

2.使用中造成的一切后果，本人概不负责。
