# Security Policy

## Supported Versions

Only the latest release of Paste Keyboard receives security fixes.

| Version | Supported |
| ------- | --------- |
| latest  | yes       |
| older   | no        |

## Scope

Paste Keyboard is a local Windows desktop tool. It simulates keyboard input from clipboard content and stores settings locally under `%APPDATA%\PasteKeyboard`. It has no network server, no remote API, and no multi-user functionality.

In-scope for security reports:

- Privilege escalation via the application
- Unintended code execution triggered by crafted clipboard content
- Unauthorized access to or manipulation of settings in `%APPDATA%\PasteKeyboard`

Out of scope:

- Denial of service or resource exhaustion
- Issues requiring physical access to the machine
- Vulnerabilities in third-party dependencies (please report those upstream)

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities, as this exposes the issue before a fix is available.

Use GitHub's private vulnerability reporting instead:
**[Report a vulnerability](https://github.com/andreas-hafner/paste_keyboard/security/advisories/new)**

This creates a private advisory visible only to you and the maintainer until it is resolved and disclosed.

Include in your report:

1. A description of the vulnerability and its potential impact
2. Steps to reproduce or a proof-of-concept
3. The version of Paste Keyboard you tested against

You can expect an acknowledgement within **5 business days** and a status update within **14 days**.
