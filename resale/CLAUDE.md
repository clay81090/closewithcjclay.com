# Guardrails for the Resale build

You are the builder. You do not decide product, scope, or architecture. Those are already decided in `resale/PLAN.md`.

- Edit files only inside `resale/`, and only the app files named in the plan.
- Do not edit `resale/PLAN.md`, `resale/CLAUDE.md`, `resale/BUILD_TASK.md`, `resale/claude-settings.json`, `resale/start-build.sh`, or anything in `resale/seed/`.
- Do not edit, move, rename, format, or delete any HTSA page, close script, template, rule, or other file outside `resale/`.
- Do not run `git add`, `git commit`, `git push`, `git reset`, `git checkout`, or `git restore`.
- Do not invent a sold price, a comp, or a source URL.
- Do not put an API key in any file.
- Do not add a server, a database host, Expo, or a build step.
- If a step in the plan seems wrong, follow the plan and note the concern in `resale/BUILD_REPORT.md`.
- Do not ask questions. Build.
