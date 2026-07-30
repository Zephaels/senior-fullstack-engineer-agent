# Host Validation Matrix

| Host | Installation path | Required evidence | Current status |
|---|---|---|---|
| Codex local marketplace | `~/plugins/<name>` + `~/.agents/plugins/marketplace.json` | file copy, manifest match, marketplace entry | PASS (isolated HOME) |
| Codex CLI/App runtime | Plugins UI / fresh session | host version, plugin enabled, Skill list, low-risk prompt | BLOCKED |
| ChatGPT web/desktop | Plugin Directory / Workspace settings | listing, installation policy, role, invocation | BLOCKED |
| Workspace-admin deployment | Workspace settings > Plugins | role policy and app permission review | BLOCKED |

## Codex runtime test

1. Install the repository marketplace or personal marketplace entry.
2. Enable the plugin in Plugins UI.
3. Start a fresh session.
4. Record Codex version and operating system.
5. Verify the router and at least three specialist Skills are discoverable.
6. Run one low-risk prompt and preserve the complete transcript.
7. Test uninstall, reinstall and upgrade from the previous RC.

## ChatGPT test

1. Review the Plugin listing, included Skills and any app requirements.
2. Confirm workspace role and installation policy.
3. Install/connect only through an eligible Plugin Directory or approved workspace flow.
4. Invoke a low-risk analysis-only prompt.
5. Confirm the plugin grants no data access beyond separately approved apps.

## Installation attempts in this environment

- `npm view/install @openai/codex`: blocked because the sandbox npm registry returned `404`.
- Official `https://chatgpt.com/codex/install.sh`: blocked because the sandbox could not resolve `chatgpt.com`.
- These are environment/network blockers, not evidence that the official installers are invalid.
