# Contributing to flashcards_backend

Thanks for your interest in contributing! Your help makes this project better for everyone.

## 📣 Before you begin

- **Discuss large changes first:**  
  Please open a [GitHub issue](../../issues) or discuss with maintainers before starting work on substantial features or breaking changes.
- **Read our [Code of Conduct](./CODE_OF_CONDUCT.md):**  
  You agree to follow it in all interactions and PRs.

---

## 🌳 Branching & Workflow

We use the following branching strategy:

- **`main`:** Production releases only
- **`dev`:** All ongoing development
- **Feature/Task branches:** Based on `dev`, named using:
    - General: `feature/<short-description>`
    - Bugfix: `bug/<short-description>`
    - Hotfix: `hotfix/<short-description>`
    - Chore/tooling: `chore/<short-description>`
    - **Or JIRA prefix:** e.g., `FA-21/feature/add-user-auth` if using issue/task tracking

**Examples:**  
- `feature/add-registration-flow`  
- `bug/fix-session-timeout`  
- `FA-34/feature/async-support`

### ⛑️ Rules:

- *Do NOT push or merge directly to `dev` or `main`.*
- *All merges must be done through Pull Requests (PRs) and require at least one approval from a maintainer (currently only allowed by repo admins/owners).*
- Merge feature/bug/hotfix/chore branches → `dev`
- When ready for production, merge from `dev` → `main`
- Keep branches focused and named clearly

---

## 🧩 Pull Request Process

1. **Ensure code is tested** and passes CI before submitting a PR.
2. **Update documentation:**  
   - Add/modify relevant docstrings in code.
   - Update `README.md` for public API, new features, breaking changes, new env vars, config options, etc.
3. **Versioning:**  
   - We use [Semantic Versioning](https://semver.org/) (SemVer). If your change affects API or functionality for users, suggest a version bump in the PR notes.
4. **Review & Approval:**  
   - At *least one approved review* from a maintainer is required. If you lack permissions to merge, tag a maintainer for review/merge.

---

## 📝 Coding Standards

- Write clear, concise commit messages.
- Use [PEP8](https://www.python.org/dev/peps/pep-0008/) style for Python code.
- Keep PRs scoped (prefer several small, reviewable changes over one huge PR).

---

## ❌ What not to do

- Don’t merge or push to `dev` or `main` directly.
- Don’t open public issues for security vulnerabilities—[see our security policy](./SECURITY.md).
- Don’t submit PRs without required tests/documentation.

---

## 🤝 Code of Conduct

Everyone is expected to follow our [Code of Conduct](./CODE_OF_CONDUCT.md), which is adapted from the [Contributor Covenant v1.4](http://contributor-covenant.org/version/1/4).

---

If you have questions, reach out via issues or contact a maintainer.

Welcome to the project! 🚀
