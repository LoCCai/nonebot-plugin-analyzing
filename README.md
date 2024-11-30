<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-resolver2/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-resolver2/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-resolver2

_✨ NoneBot 插件简单描述 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/fllesser/nonebot-plugin-resolver2.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-resolver2">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-resolver2.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

这是一个 nonebot2 插件项目的模板库, 你可以直接使用本模板创建你的 nonebot2 插件项目的仓库

<details open>
<summary>模板库使用方法</summary>

1. 点击 [![start-course](https://user-images.githubusercontent.com/1221423/235727646-4a590299-ffe5-480d-8cd5-8194ea184546.svg)](https://github.com/new?template_fllesser=A-kirami&template_name=nonebot-plugin-resolver2&fllesser=%40me&name=nonebot-plugin-&visibility=public) 创建仓库
2. 在创建好的新仓库中, 在 "Add file" 菜单中选择 "Create new file", 在新文件名处输入`LICENSE`, 此时在右侧会出现一个 "Choose a license template" 按钮, 点击此按钮选择开源协议模板, 然后在最下方提交新文件到主分支
3. 全局替换`fllesser`为仓库所有者ID; 全局替换`nonebot-plugin-resolver2`为插件名; 全局替换`nonebot_plugin_resolver2`为包名; 修改 python 徽标中的版本为你插件的运行所需版本
4. 修改 README 中的插件名和插件描述, 并在下方填充相应的内容

</details>

> [!NOTE]
> 模板库中自带了一个发布工作流, 你可以使用此工作流自动发布你的插件到 pypi

<details>
<summary>配置发布工作流</summary>

1. 前往 https://pypi.org/manage/account/#api-tokens 并创建一个新的 API 令牌。创建成功后不要关闭页面，不然你将无法再次查看此令牌。
2. 在单独的浏览器选项卡或窗口中，打开 [Actions secrets and variables](./settings/secrets/actions) 页面。你也可以在 Settings - Secrets and variables - Actions 中找到此页面。
3. 点击 New repository secret 按钮，创建一个名为 `PYPI_API_TOKEN` 的新令牌，并从第一步复制粘贴令牌。

</details>

> [!IMPORTANT]
> 这个发布工作流需要 pyproject.toml 文件, 并且只支持 [PEP 621](https://peps.python.org/pep-0621/) 标准的 pyproject.toml 文件

<details>
<summary>触发发布工作流</summary>
从本地推送任意 tag 即可触发。

创建 tag:

    git tag <tag_name>

推送本地所有 tag:

    git push origin --tags

</details>

## 📖 介绍

这里是插件的详细介绍部分

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-resolver2

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-resolver2
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-resolver2
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-resolver2
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-resolver2
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_resolver2"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| NICKNAME | 是 | 无 | nonebot2内置配置，可作为解析结果消息的前缀 |
| r_xhs_ck | 否 | 无 | 配置说明 |
| r_douyin_ck | 是 | 无 | 配置说明 |
| r_bili_ck | 否 | 无 | B站 cookie, 必须含有 SESSDATA 项 填写后可附加 B 站 ai 总结 |
| r_ytb_ck | 否 | 无 | youtube cookie, youtube 视频因人机检测下载失败，可填写 |
| r_is_oversea | 否 | False | 海外服务器部署，或者使用了透明代理，设置为 True |
| r_proxy | 否 | 'http://127.0.0.1:7890' | # 代理 r_is_oversea=False 时生效 |
| r_video_duration_maximum | 否 | 480 | 视频最大解析长度，默认480s为8分钟，计算公式为480s/60s=8mins |
| r_black_resolvers | 否 | 无 | 全局禁止的解析，示例 r_black_resolvers=["bilibili", "douyin"] 表示禁止了哔哩哔哩和抖 bilibili,douyin,tiktok,acfun,twitter,xhs,ytb.ncm,kugou,weibo,kugou |

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 开启解析 | SUPERUSER/OWNER/ADMIN | 是 | 群聊 | 开启解析 |
| 关闭解析 | SUPERUSER/OWNER/ADMIN | 是 | 群聊 | 关闭解析 |
| 查看关闭解析 | SUPERUSER | 否 | - | 获取已经关闭解析的群聊 |

### 效果图
