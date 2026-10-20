# Security policy

This independent project is maintained on a best-effort basis. The currently tested series is 0.4.x with the exact Typeless 2.2.0 Linux build identified in `runtime/prepare.py`. An unsupported vendor fingerprint disables the answer-card and autostart-generation runtime patches; base input compatibility can still run.

Report suspected vulnerabilities through [GitHub private vulnerability reporting](https://github.com/howiehu/typeless-omarchy/security/advisories/new). If the private form is unavailable, open an issue asking for a private contact without disclosing exploit details.

Do not publish account data, transcripts, cookies or tokens. A useful private report describes affected versions, a minimal synthetic reproduction and the impact. No response-time or coordinated-disclosure deadline is guaranteed.

The bridge uses a private per-user socket and rejects password/sensitive input contexts. These checks do not control all fallback behavior inside the proprietary application. A preflight focus check also cannot guarantee that focus stays unchanged before insertion. See the limitations in the README.
