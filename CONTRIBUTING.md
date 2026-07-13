# Contributing

Thanks for contributing. This doc covers what you need to get set up and how to get a change merged.

## Getting Started

```bash
git clone https://github.com/creova-gif/Akili-Core.git
cd Akili-Core
pip install -r requirements.txt --break-system-packages
cp .env.example .env
# fill in your own API keys/credentials in .env — this file is git-ignored, never commit it
```

## Before You Open a Pull Request

1. **Branch from `main`** — use a descriptive branch name, e.g. `fix/rate-limit-bug` or `feat/add-new-agent`.
2. **Keep PRs focused** — one logical change per PR.
3. **Never commit secrets** — no `.env` files, API keys, or credentials of any kind. This repo has had a real leaked-credential incident in the past (since fully remediated) — take this seriously.
4. **Write a clear PR description** — what changed, why, and how you tested it.

## Code Review

- All PRs require review before merging to `main` — direct pushes to `main` are blocked.
- Address review feedback with new commits rather than force-pushing.

## Security

Found a security issue? See [`SECURITY.md`](./SECURITY.md) — don't open a public issue for vulnerabilities.

## Questions

Open an issue or reach out to the maintainer directly if you're unsure where to start.

## AI-Assisted Contributions

AI tools (Copilot, Claude, ChatGPT, etc.) may be used to assist with contributions,
but every submission must meet the same bar as human-authored code:

- A human contributor must review, understand, and take ownership of any
  AI-assisted change before opening a PR.
- PRs should be described in terms of *what changed and why*, not how they
  were generated.
- Commit history should be clean and logical — squash exploratory or
  AI-iteration commits before merging to main.
- Security-critical paths, core architecture decisions, and public-facing
  API contracts require human-authored review and rationale, regardless of
  drafting assistance used.

We welcome AI-assisted contributions in this spirit. What we don't accept
is unreviewed, low-effort, or "drive-by" AI-generated PRs.
