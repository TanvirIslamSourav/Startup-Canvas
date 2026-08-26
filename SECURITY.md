# Security Policy

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| `main`  | ✅ Active          |
| latest release tag | ✅ Active |
| older releases | ❌ End-of-life |

We only backport security fixes to the most recent release. Please
[upgrade](docs/DEPLOYMENT.md) before opening a security report.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security problems.**

Send a private report to **security@startup-canvas.example** with:

1. A clear, reproducible description of the issue.
2. The affected component (frontend, backend, docker, docs, …).
3. The commit hash or release tag you observed the issue on.
4. Any proof-of-concept code or commands (in a password-protected archive
   if it could be weaponised).
5. Your name / handle if you'd like credit in the advisory.

We aim to acknowledge new reports within **2 business days** and to provide a
fix or mitigation plan within **10 business days**, depending on severity.

## Disclosure process

1. Reporter and maintainers agree on a coordinated disclosure date.
2. Maintainers prepare a fix and a release on a private branch.
3. CVE assignment is requested (via GitHub Security Advisories) if the
   issue warrants it.
4. On the agreed date, the advisory, the fix release, and the credit
   announcement are published together.
5. Reporter is credited in `CHANGELOG.md` and the GitHub advisory.

## Out-of-scope

- Vulnerabilities in third-party services we depend on (PostgreSQL,
  nginx, Node.js, Python). Please report those upstream.
- Theoretical issues with no demonstrable impact.
- Issues requiring physical access to a user's device.
- "Best practice" suggestions without a concrete exploit path.

Thank you for helping keep Startup Canvas and its users safe.