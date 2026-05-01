# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest (`main`) | ✅ |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, report them privately via [GitHub's private vulnerability reporting](https://github.com/JoeRyanMBA/StructuredDocs/security/advisories/new).

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or proof-of-concept code
- Any suggested mitigations

You can expect an acknowledgement within **72 hours** and a fix or mitigation plan within **14 days** for confirmed issues.

## Security Best Practices for Self-Hosting

- Always set strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`
- Never commit `.env` files to version control
- Use HTTPS in production (set `SESSION_COOKIE_SECURE=1`)
- Rotate `ADMIN_API_KEY` immediately after first setup
- Keep SMTP credentials scoped to the minimum required permissions
- Review `SPACES_KEY` / `SPACES_SECRET` bucket permissions; restrict to the required bucket only
