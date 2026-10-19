# Upstream and public announcement drafts

These are prepared messages. Their presence in this repository does not mean that Typeless has been contacted or has accepted the fixes.

Publication status: the maintainer posted on X at https://x.com/howiehu/status/2112052342963192284 . Email outreach was cancelled; the email text below is retained for reference only and is not scheduled for delivery.

## Typeless support email — reference only, not to be sent

Recipient: `hello@typeless.com`, as listed in the [official support FAQ](https://www.typeless.com/help/faqs).

Subject: Linux 2.2.0 compatibility report: Omarchy/Hyprland + Fcitx5

Hello Typeless team,

I use Typeless 2.2.0 on Omarchy 4.0.5 / Hyprland 0.56.2 with Fcitx5 5.1.23. I have published an independent compatibility project with reproducible cases and tested workarounds for:

- Dictation delivery in Foot while retaining the selected Shuangpin/English input method.
- Native-Wayland HUD and interactive answer-card behavior across workspaces.
- Ask Anything completions classified as replace when there is no eligible input target: show the official answer card rather than silently attempting a paste.
- Rectangular text displacement/flicker while scrolling answer cards; an app-scoped software-rendering comparison resolved it on the test desktop.

Technical report, evidence and limitations:
https://github.com/howiehu/typeless-omarchy/blob/v0.4.3/docs/upstream-report.md

Source and pre-release:
https://github.com/howiehu/typeless-omarchy
https://github.com/howiehu/typeless-omarchy/releases/tag/v0.4.3

Omarchy packaging contribution:
https://github.com/omacom/omarchy-pkgs/pull/1294

The project’s original contributions are offered under MIT only to the extent contributors can grant those rights; third-party material is not relicensed. The repository distributes neither the proprietary app nor a patched application bundle. The application-side workaround generates a private runtime copy on the user's machine only after exact source fingerprint checks; the installed vendor files are unchanged. Local generation does not establish vendor permission or legal clearance; the restrictions in your Terms of Service remain relevant. Input, answer display and scrolling were confirmed on the test desktop, but I am not claiming general Wayland/GPU support or that a previous application disappearance was fixed.

Could you route this to the Linux desktop/input team and advise on your preferred contribution process or supported extension interfaces? I would be happy to help turn the reproductions and independent implementation into official source-level fixes, so users no longer need the private-runtime workaround.

Thank you,
Hao Hu
https://github.com/howiehu

## X draft

Suggested mention: `@typelessdotcom`. Verify the account on X before posting; direct profile verification was unavailable during preparation.

> Built Typeless-Omarchy for Typeless 2.2.0 on Omarchy/Hyprland: Fcitx dictation without IME switching, answer-card recovery, and a scrolling workaround. Pre-release, source + repros: https://github.com/howiehu/typeless-omarchy @typelessdotcom

A follow-up can link the technical report and explain that this is an independent, version-specific compatibility project. Describe the rendering change as a workaround, not an upstream GPU fix. Use synthetic-text footage if adding a demo.
