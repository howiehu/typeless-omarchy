# Typeless-Omarchy

面向 Omarchy / Hyprland / Fcitx5 的独立兼容层。当前为 **0.4.2 预发布版**，只在 x86_64、Typeless 2.2.0 的指定构建上验证过；并非 Typeless 或 Omarchy 官方项目。

完整安装、构建与限制说明以 [英文 README](README.md) 为准。

## 已实现

- 通过被动 Fcitx 模块投递语音文字，保留当前双拼或英文输入法。
- 使用原生 Wayland 启动，修正透明状态浮层的边框和焦点。
- 录音状态和官方答案卡片跨工作区显示；答案卡片可点击、复制。
- “问问题”被判为替换文字但找不到合适输入框时，显示官方答案卡片。
- 仅为 Typeless 默认启用软件渲染，缓解实测的滚动方块错位与闪烁。

保留官方主界面、托盘、登录和引导；不增加自建托盘或常驻服务。输入兼容、答案卡片和滚动已获得本机用户实际确认，尚不代表所有 Wayland / GPU 环境均适用。

## 安装与卸载

先单独安装官方 `typeless-bin`，再按照 [安装说明](README.md#install-on-omarchy) 构建兼容包。安装后完全退出 Typeless，并以普通桌面用户运行：

```sh
typeless-omarchy-setup
```

这一步会短暂重启 Fcitx，保留先前选中的输入法，然后从应用菜单启动 Typeless-Omarchy。已有的官方自动启动项不会自动改写。

卸载前先退出 Typeless：

```sh
typeless-omarchy-setup --remove
sudo pacman -R typeless-omarchy
```

## 重要边界

官方安装文件不会被改写。答案恢复通过本机私有运行副本实现，严格核对官方代码指纹；生成的副本不随本项目发布。未知版本退回基础输入兼容模式。

软件渲染可能增加 CPU 占用。退出已运行实例后，可用 `TYPELESS_OMARCHY_GPU=1 typeless-omarchy` 恢复硬件渲染，或用 `TYPELESS_OMARCHY_BASE_ONLY=1 typeless-omarchy` 跳过答案恢复副本。

兼容层不读取账户或历史数据库来恢复答案。富文本编辑、焦点在投递前发生变化及官方独立回退行为仍有限制；此前程序退出问题也没有确认根因。请勿提交含账户信息、令牌或私人语音内容的日志与截图。

[版本发布](https://github.com/howiehu/typeless-omarchy/releases) · [验证记录](docs/validation.md) · [官方技术报告](docs/upstream-report.md) · [贡献指南](CONTRIBUTING.md)
