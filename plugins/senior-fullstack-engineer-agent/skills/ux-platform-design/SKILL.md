---
name: ux-platform-design
description: Designs coherent product experiences across web, mobile, tablet, desktop, and supported native platforms while preserving shared semantics and adapting navigation, input, density, system integration, states, accessibility, and motion. Use before meaningful UI flows, design systems, responsive, or cross-platform changes.
---

# UX and Platform Design

## Purpose

Translate approved product requirements into an executable experience specification that keeps the product core consistent while adapting each platform to its interaction model, screen, windowing, lifecycle, input methods, and system conventions.

UX design defines user tasks, information architecture, navigation, states, interaction behavior, accessibility, content, and platform adaptation. It does not write production UI code unless a separate implementation workflow is authorized.

## When to Use

Use this workflow when:

- Designing a new user flow, screen set, workspace, navigation model, dashboard, editor, onboarding, settings, or account experience.
- A capability spans Web, mobile, tablet, desktop, wearable, or multiple window sizes.
- A phone layout is at risk of being enlarged for tablet or a desktop workflow compressed into mobile.
- Loading, empty, error, permission, offline, synchronization, conflict, success, disabled, or read-only behavior is unclear.
- Keyboard, pointer, touch, pen, drag-and-drop, shortcuts, menus, windows, or system integrations matter.
- A design system or reusable component behavior needs definition.
- Accessibility, localization, reduced motion, high contrast, or responsive behavior needs specification.
- A Figma or visual design must be translated into product- and platform-correct behavior.

## Do Not Use

Do not use this workflow to:

- Add decorative animation without a user or system purpose.
- Mechanically reproduce pixels while ignoring accessibility, platform behavior, or product semantics.
- Implement code from an already approved and current UX specification; use `incremental-implementation`.
- Replace user research or product discovery.
- Declare support for a platform that cannot be tested or is outside scope.

## Preconditions

Read and apply:

- [`../../core/constitution.md`](./references/core/constitution.md)
- [`../../core/task-classifier.md`](./references/core/task-classifier.md)
- [`../../core/decision-policy.md`](./references/core/decision-policy.md)
- `product-discovery` when user value or task is unclear
- `requirements-specification`
- `repository-discovery` for existing products
- `source-verification` for current platform guidelines and component behavior

Inputs may include approved requirements, user journeys, platform targets, design system, content, Figma files, current UI, accessibility requirements, analytics, and technical constraints.

## Governing Principle

```text
Unify the product core; adapt the platform experience.
```

Must remain consistent across platforms:

- Product purpose and user goals.
- Feature semantics and business rules.
- Data model, permissions, user state, and operation results.
- Brand language and critical terminology.

May adapt by platform:

- Layout and navigation.
- Information density and window structure.
- Controls and input methods.
- Menus, toolbars, shortcuts, hover, context menus, drag-and-drop, and multi-window behavior.
- Platform integrations, interruption handling, background behavior, and state restoration.

## Required Depth by Task Class

### Q — Quick Patch

Confirm the current design-system pattern, affected state, focus behavior, contrast, localization, and platform impact.

### S — Standard Change

Define the task flow, responsive/platform variants, complete state model, content, accessibility, and acceptance criteria.

### C — Complex Feature

Add information architecture, navigation, multi-platform classification, design-system changes, interaction model, keyboard/touch/pointer behavior, offline/sync/conflict handling, analytics, and usability validation.

### X — Critical Change

Add safety, consent, privacy, payment, destructive action, administrative, accessibility, legal-content, recovery, audit, and independent design review requirements.

## Workflow

### Step 1: Establish the user task

Define:

- Actor and goal.
- Trigger and context.
- Entry points.
- Primary path.
- Alternative and recovery paths.
- Completion state and next likely action.
- Frequency, urgency, and error consequence.

Do not start from screen count or component choice.

### Step 2: Define information architecture

Specify:

- Objects and their relationships.
- Primary and secondary information.
- Grouping, hierarchy, labels, search, filtering, sorting, and navigation.
- What persists across sessions, tabs, windows, devices, and accounts.
- What users can safely hide, archive, undo, restore, or revisit.

Use user language and existing canonical terms.

### Step 3: Classify platform behavior

For each capability mark:

- `Shared` — same product meaning and behavior.
- `Adapted` — same capability, platform-specific presentation or interaction.
- `Platform Only` — valuable only on a specific platform.
- `Not Applicable` — intentionally unsupported.

Record the reason. Do not declare a platform complete based only on a responsive mockup.

### Step 4: Design navigation by platform

Consider:

- Mobile: touch-first, short paths, single-hand reach, soft keyboard, interruption, permissions, weak network, orientation.
- Tablet: multi-column layouts, split view, resizable windows, keyboard, pointer, pen, drag-and-drop, preserved task state.
- Desktop: windows, menus, toolbars, shortcuts, context menus, hover, precise input, multi-select, drag-and-drop, high information density, state restoration.
- Web: responsive layout, keyboard navigation, deep links, refresh recovery, history navigation, session expiry, weak-network retry, target browser support.
- Wearable or spatial: only when the capability is timely, glanceable, short, and materially improved by the platform.

### Step 5: Define the complete state model

For every screen, component, or flow consider:

- Initial/default.
- Loading and progressive loading.
- Empty and first-use.
- Partial data.
- Error and recovery.
- Offline and reconnecting.
- Synchronizing and conflict.
- Permission denied and authentication expired.
- Disabled and read-only.
- Success and confirmation.
- Destructive pending, undo, recovery, and history.
- Long-running, canceling, retrying, timed out, and backgrounded.

Do not communicate state only through color.

### Step 6: Define interaction behavior

Specify:

- Focus, selection, hover, pressed, drag, drop, resize, reorder, and multi-select.
- Keyboard order and shortcuts.
- Touch targets and gestures.
- Pointer precision and context actions.
- Interruptibility and cancellation.
- Feedback, latency masking, optimistic behavior, and reconciliation.
- Confirmation, undo, recycle bin, version history, or recovery for irreversible actions.

High-frequency interactions should avoid ornamental delay. Motion should explain change, preserve spatial continuity, or provide feedback.

### Step 7: Define design-system impact

Identify:

- Semantic tokens.
- Typography and content hierarchy.
- Spacing and layout primitives.
- Component variants and states.
- Icon meaning and text alternatives.
- Theme, dark mode, high contrast, reduced motion, and localization behavior.
- New primitives versus extensions of existing components.

Prefer system controls and the current design system. Avoid scattered literal values and parallel component libraries.

### Step 8: Define accessibility

Specify and test:

- Semantic structure and accessible names.
- Keyboard operation and visible focus.
- Screen-reader order, announcements, and errors.
- Contrast and non-color state indicators.
- Font scaling, zoom, reflow, long text, and localization.
- Touch target size and motor accessibility.
- Reduced motion and non-motion alternatives.
- Captions, transcripts, and media alternatives where relevant.
- Timeouts, cognitive load, predictable navigation, and error prevention.

Accessibility is part of the definition, not a post-build checklist.

### Step 9: Define content and error language

Content must state:

- What happened.
- Why it matters when known.
- What the user can do next.
- What data or action is affected.

Do not expose stack traces, internal identifiers, secret details, or blame the user. Confirm destructive outcomes in concrete terms.

### Step 10: Define responsive and adaptive rules

Specify behavior based on available space and capability rather than named device models alone:

- Breakpoints or container rules.
- Reflow, collapse, prioritization, and progressive disclosure.
- Persistent versus temporary navigation.
- Column count and pane behavior.
- Window resizing and state preservation.
- Large data, tables, editors, charts, and command surfaces.

### Step 11: Define validation

Choose appropriate evidence:

- Clickable prototype or low-cost flow simulation.
- Design review against requirements.
- Accessibility review.
- Usability session.
- Visual and interaction regression.
- Platform-specific runtime QA.
- Analytics or experiment after release.

### Step 12: Produce the UX Specification

```markdown
# UX and Platform Specification

## User Task and Success

## Information Architecture

## User Flow and Recovery Paths

## Platform Classification Matrix

## Navigation and Layout by Platform

## Screen / Component State Model

## Interaction and Input Model

## Design System Changes

## Accessibility Requirements

## Content and Error Language

## Responsive / Windowing Rules

## Analytics and Feedback

## Validation Plan

## Risks, Non-goals, and Open Questions
```

## Quality Gates

Pass only when:

- Product semantics are consistent across platforms.
- Platform differences are intentional and documented.
- Complete state and recovery behavior is defined.
- Accessibility is testable.
- Navigation and input match target platform expectations.
- Design-system impact is bounded.
- Destructive and long-running actions have feedback, cancellation, and recovery where applicable.
- Unsupported platforms are not claimed as complete.

## Failure and Return Routes

- User goal or value unclear → `product-discovery`.
- Business behavior unclear → `intent-interview` or `requirements-specification`.
- Current UI or design system unknown → `repository-discovery`.
- Current platform guidance uncertain → `source-verification`.
- Architecture cannot support required state or platform behavior → `architecture-design`.
- UX approved → `implementation-planning`.
