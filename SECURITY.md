# Security Policy

## Supported Versions

Only the latest release is supported. Please update to the latest version before reporting an issue.

## Reporting a Vulnerability

This integration only performs an unauthenticated HTTPS GET of the public CSV at `www.bfe-ogd.ch` (SFOE Open Government Data) — it does not handle credentials or personal data, sends nothing besides that request to any endpoint, and has no write access to any external system. If you still believe you have found a security issue (e.g. in how data is parsed or how entities are exposed), please report it privately via [GitHub Security Advisories](../../security/advisories/new) rather than opening a public issue.

For anything that is not security-sensitive (bugs, feature requests), please use the regular [Issues](../../issues) tab instead.
