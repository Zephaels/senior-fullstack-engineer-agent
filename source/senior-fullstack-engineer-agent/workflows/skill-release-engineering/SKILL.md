---
name: skill-release-engineering
description: Packages, validates, versions, documents, and publishes an Agent Skill or Codex plugin as a reproducible general availability. Use when preparing a skill repository for distribution, generating plugin manifests or marketplace entries, building release archives, creating checksums or SBOMs, defining CI/release workflows, or deciding whether a skill version is ready for RC or GA. Do not use for deploying the software product that the skill helps build; use release-deployment for that.
---

# Skill Release Engineering

## Purpose

Turn an authored Skill tree into a reproducible, reviewable, installable, and traceable release. This workflow governs the Skill or plugin package itself, not the application being developed by that Skill.

## Use This Skill When

- Building a Codex or ChatGPT plugin from one or more Agent Skills.
- Preparing a general availability, tag, changelog, distribution archive, or marketplace entry.
- Validating `.codex-plugin/plugin.json`, `SKILL.md`, evaluation assets, links, scripts, licenses, and source notices.
- Generating checksums, file manifests, software bills of materials, or artifact provenance configuration.
- Installing, upgrading, verifying, or uninstalling a local development plugin.
- Assessing whether an Alpha, Beta, RC, or GA release gate is satisfied.

## Do Not Use

- To deploy a user's web, mobile, desktop, cloud, database, or AI product. Use `release-deployment`.
- To claim model quality without executing real model evaluations. Use `skill-evaluation`.
- To choose product behavior or user requirements.
- To change license terms without an explicit owner decision.

## Required Inputs

- Release target and version.
- Authoring source tree.
- Target hosts and distribution formats.
- License decision or explicit unresolved-license status.
- Validation and evaluation requirements.
- Existing release history, when updating.

## Release Classes

| Class | Meaning | Minimum evidence |
|---|---|---|
| Alpha | Structure and workflow design are still changing | Static validation and transparent limitations |
| Beta | Main workflows are present and usable | Trigger/behavior evaluations plus installation tests |
| RC | Intended release content is frozen except defects | Full static validation, package verification, security review, reproducible build, unresolved blockers listed |
| GA | Public production release | RC evidence plus real-host tests, real-model regression, finalized license/support/security/publishing metadata |

A release label may not exceed its evidence. A package with blocked real-model evaluation is not GA.

## Workflow

### 1. Freeze the release scope

Record:

- Version and release class.
- Included Skills and excluded work.
- Supported hosts.
- Compatibility assumptions.
- Known upstream limitations.
- Whether public marketplace publication is in scope.

Require a version change whenever distributed content changes. Do not rely on a plugin cache noticing unversioned content changes.

### 2. Validate source Skills

For every Skill:

- Directory name matches frontmatter `name`.
- `description` defines both capability and trigger boundary.
- YAML frontmatter parses.
- Relative links resolve.
- No placeholder tokens remain.
- Script syntax and declared dependencies are valid.
- Positive and negative trigger cases exist for release-critical Skills.
- Tool, network, write, Git, deployment, and cost side effects are disclosed.

Return source defects to the owning workflow. Do not repair behavioral ambiguity in the release pipeline.

### 3. Compile host-specific distributions

For a Codex plugin:

- Place the manifest at `.codex-plugin/plugin.json`.
- Keep the plugin folder name and manifest `name` identical.
- Use strict semantic versioning.
- Include only supported manifest fields.
- Point `skills` to `./skills/`.
- Include `apps` or `mcpServers` only when their companion files exist.
- Keep hooks out of the manifest unless the current accepted schema explicitly supports them.
- Ensure all paths stay inside the archive.
- Generate optional `agents/openai.yaml` metadata only with accepted fields.

For a marketplace repository:

- Store plugins below `plugins/<plugin-name>/`.
- Store the marketplace at `.agents/plugins/marketplace.json`.
- Use `./plugins/<plugin-name>` as the local source path.
- Include installation, authentication, and category policy fields.

### 4. Create release documentation

At minimum:

- `README.md`
- `CHANGELOG.md`
- License file
- `NOTICE.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- Compatibility and known-issues documentation
- Release process and evaluation documentation

Do not invent contact addresses, repository URLs, privacy-policy URLs, terms URLs, or support guarantees. Omit optional manifest URLs until real HTTPS destinations exist.

### 5. Build reproducible artifacts

- Build from a clean source snapshot.
- Exclude caches, local credentials, virtual environments, temporary outputs, and prior archives.
- Sort archive paths deterministically.
- Normalize timestamps where the packaging implementation supports it.
- Generate SHA-256 checksums.
- Generate a file manifest and SBOM.
- Record source version, build timestamp, tool version, and validation results.

### 6. Run release validation

Validate independently:

- Source Skill tree.
- Plugin manifest contract.
- Marketplace contract.
- All JSON and YAML.
- Markdown links.
- Script syntax.
- Archive integrity.
- Checksums and file manifests.
- No secret-like files or obvious credential patterns.
- License and attribution state.
- Evaluation state.

Use `preflight-verification` for evidence discipline and `security-engineering` for release supply-chain review.

### 7. Run evaluation gates

Use `skill-evaluation` to execute:

- Trigger evaluations.
- Negative trigger evaluations.
- Behavior evaluations.
- Pressure evaluations.
- Cross-skill regression.
- Real-host installation and discovery tests.
- Real-model RED → GREEN → Regression tests.

Mock transport proves the harness only. It does not count as model evidence.

### 8. Publish or block

A release report must state one of:

- `RC_READY`
- `RC_READY_WITH_ACCEPTED_RISK`
- `RC_BLOCKED`
- `GA_READY`
- `GA_BLOCKED`

A public release must be blocked when the license, security reporting path, required public URLs, host installation, or real-model evidence is unresolved.

### 9. Archive evidence

Record:

- Release version and commit or source digest.
- Package hashes.
- Validation report.
- SBOM.
- Evaluation report.
- Known issues.
- Accepted risks and owner.
- Rollback or unpublish procedure.

Update `project-state-handoff` with release status and remaining blockers.

## Output Contract

```yaml
release:
  version: 0.0.0
  class: rc
  source_digest: sha256:...
  packages:
    - path: package.zip
      sha256: ...
  validation:
    source: pass
    plugin: pass
    marketplace: pass
    archives: pass
  evaluation:
    trigger: pass
    behavior: pass|blocked
    real_model: pass|blocked
  legal:
    license: finalized|internal_only|blocked
    notice: complete|needs_review
  result: RC_READY|RC_READY_WITH_ACCEPTED_RISK|RC_BLOCKED|GA_READY|GA_BLOCKED
  blockers: []
```

## Prohibited Behaviors

- Publishing a changed plugin without a version bump.
- Calling an archive reproducible without testing reproducibility.
- Counting mock output as real-model evidence.
- Removing source notices to simplify distribution.
- Adding unsupported fields to `plugin.json`.
- Bundling secrets, credentials, customer data, local caches, or internal paths.
- Claiming public GA while the license is an internal preview license.
- Silently swallowing validator or archive errors.
