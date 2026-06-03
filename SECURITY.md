# Security Policy

## Reporting a Vulnerability

Please do not open a public issue for a security vulnerability.

Use GitHub private vulnerability reporting if it is enabled for the repository.
If private reporting is not available, open a minimal public issue asking for a
private contact path and do not include exploit details.

## Scope

WebDownloader fetches and writes content from remote websites. Treat downloaded
files as untrusted input, and inspect them before serving or opening them in a
privileged environment.
