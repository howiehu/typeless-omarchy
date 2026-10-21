# Typeless-Omarchy

面向 Omarchy / Hyprland / Fcitx5 的独立兼容层。当前为 **0.5.1 正式版**，已在 x86_64、Typeless 2.2.1 的指定构建上验证原生输入；保留 2.2.0 补丁配置。并非 Typeless 或 Omarchy 官方项目。

2.2.1 已通过实际原生库的 GTK／跨工作区 Foot 输入、双拼保持和空闲浮层下的真实鼠标点击测试。此前用户对语音混合输入、结果卡片及滚动的确认来自 2.2.0 环境，不代表已完成 2.2.1 的全部端到端人工验收；详见[验证记录](docs/validation.md)。

完整安装、构建与限制说明以 [英文 README](README.md) 为准。

## 已实现

- 通过被动 Fcitx 模块投递语音文字，保留当前双拼或英文输入法。
- 使用原生 Wayland 启动，修正透明状态浮层的边框；录音浮层可点击取消／确认，并把键盘焦点还给同工作区内仍可见的原窗口，恢复时不移动鼠标；通过控件几何信息使透明区域穿透鼠标；仅在存在控件时启用合成器内部的 8 毫秒检查。
- 使用同名兼容入口替代官方菜单入口，只保留一个名为 Typeless 的可见图标；保护该入口不被官方清理，登录回调与自启仍经过兼容启动器。
- 录音状态和官方答案卡片跨工作区显示；答案卡片可点击、复制。
- “问问题”被判为替换文字但找不到合适输入框时，显示官方答案卡片。
- 仅为 Typeless 默认启用软件渲染，缓解实测的滚动方块错位与闪烁。

保留官方主界面、托盘、登录和引导；不增加自建托盘或常驻服务。输入兼容、答案卡片和滚动已获得本机用户实际确认，尚不代表所有 Wayland / GPU 环境均适用。

应用内 Debian 更新下载、安装和重复更新提示已停用；在“关于”中手动检查时，会说明通过 Omarchy/AUR 更新。首次登录及引导继续使用官方流程。

## 安装与卸载

先单独安装官方 `typeless-bin`，再按照 [安装说明](README.md#install-on-omarchy) 构建兼容包。安装后完全退出 Typeless，并以普通桌面用户运行：

```sh
typeless-omarchy-setup
```

首次配置会短暂重启 Fcitx，保留先前选中的输入法，然后从应用菜单启动 **Typeless**。已识别的官方自启项会改为兼容启动器，并保留原有参数和启用状态；没有自启项时不会主动启用。用户自定义命令不改写。

旧版升级后，完全退出 Typeless，再运行：

```sh
typeless-omarchy-setup --repair
```

修复会迁移旧菜单配置、移除 0.4.4 的独立重复入口并保留回滚记录，不重启输入法。官方后续写入的自启命令由已核对代码指纹的运行时修补保持正确路径，官方自启开关仍可使用。卸载时恢复原菜单入口和启动命令，并保留用户后来修改的自启开关。

卸载前先退出 Typeless：

```sh
typeless-omarchy-setup --remove
sudo pacman -R typeless-omarchy
```

## 重要边界

官方安装文件不会被改写。答案恢复及自启命令生成修正通过本机私有运行副本实现，严格核对官方代码指纹；生成的副本不随本项目发布。未知版本退回基础输入兼容模式。

软件渲染可能增加 CPU 占用。退出已运行实例后，可用 `TYPELESS_OMARCHY_GPU=1 typeless-omarchy` 恢复硬件渲染，或用 `TYPELESS_OMARCHY_BASE_ONLY=1 typeless-omarchy` 跳过答案恢复及自启修补副本。

兼容层不读取账户或历史数据库来恢复答案。富文本编辑、焦点在投递前发生变化及官方独立回退行为仍有限制；此前程序退出问题也没有确认根因。请勿提交含账户信息、令牌或私人语音内容的日志与截图。

[版本发布](https://github.com/howiehu/typeless-omarchy/releases) · [验证记录](docs/validation.md) · [官方技术报告](docs/upstream-report.md) · [贡献指南](CONTRIBUTING.md)

## 版权、许可与第三方权利

Copyright (c) 2026 Hao Hu and contributors。[MIT 许可](LICENSE)仅适用于贡献者有权许可的本项目原创贡献，不会将 Typeless、第三方材料或生成的运行副本重新许可为 MIT。

[NOTICE](NOTICE)是中英文统一声明，也随兼容包安装。运行时修补使用官方程序的特定标识符和少量匹配片段；我们不主张这些第三方材料的所有权。官方安装文件保持原样，但生成的本机运行副本包含经过修改的官方材料。

“本机生成、不分发副本、核对代码指纹”均不等于获得官方授权或完成合规审查。Typeless [服务条款](https://www.typeless.com/terms)第 3、7 节包含与反向工程及修改有关的限制；本项目不宣称已确认适用的例外、许可或法律结论。

本项目未经 Typeless 或 Omarchy 背书；相关名称用于说明兼容目标，不表示获得商标许可或官方支持。完整权利边界以 LICENSE 和 NOTICE 为依据。


## 2.2.1 与后续更新

每次适配官方更新，先阅读官方[发布说明总页](https://www.typeless.com/help/release-notes)和 [Linux 发布说明](https://www.typeless.com/help/release-notes/linux)，再检查实际构建并记录查阅日期、版本、变更与验证结果，最后调整兼容层。没有详细发布说明不代表没有行为变化。具体步骤见[升级验证与发版流程](docs/releasing.md#qualify-an-official-typeless-update-first)。

2.2.1 新增了直接通过 GIO/D-Bus 查询 Fcitx 的路径。启动器仅对 Typeless 加载查询适配库，并严格限定主进程 PID、服务、接口、路径和方法；其他调用透传。原有命令行适配仍保留，不修改系统输入法或全局环境。

`python tools/check-vendor.py --archive /opt/Typeless/resources/app.asar` 可只读检查当前官方包的指纹与修补位置，不复制完整程序。每六小时的官方版本监测只读取小型版本元数据，遇到未适配版本使检查失败；不会自动接受新指纹、下载程序或发版。同版本重新构建仍需实际文件校验。我们发布已验证的兼容版后，Omarchy 配方可跟踪此项目的正式 Release；该链路需先由维护者接受 PR。详见 [2.2.1 审计](docs/typeless-2.2.1.md)。
