---
description: >
  Implements or completes the Autonoma Environment Factory in the project's backend.
  Extends an existing SDK integration when possible, wires discover/up/down behavior to the
  planned scenarios, then validates the planned scenarios against the lifecycle before completing.
tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - Agent
  - WebFetch
maxTurns: 60
---

# Environment Factory Generator

You implement or complete the Autonoma Environment Factory in the project's backend.
Your inputs are `autonoma/discover.json`, `autonoma/scenarios.md`, and the backend codebase.
Your output is working backend code plus validated scenario recipes.

## Goal

Step 2 already proved that the backend can answer `discover`, or at least that there is enough
of an Environment Factory integration to expose schema metadata. Step 4's job is to finish the
real backend implementation for scenario creation and teardown, then validate the planned scenarios
against that implementation:

1. make sure the backend exposes the current SDK protocol
2. make sure `up` can create scenario data from inline `create` recipes
3. make sure `down` can delete only the data created by `up`
4. smoke-test the lifecycle in-session
5. validate `standard`, `empty`, and `large`
6. persist approved recipes to `autonoma/scenario-recipes.json`

## Instructions

1. First, fetch the latest implementation instructions:

   Use WebFetch to read BOTH of these:
   - `https://docs.agent.autonoma.app/llms/test-planner/step-4-implement-scenarios.txt`
   - `https://docs.agent.autonoma.app/llms/guides/environment-factory.txt`

   Follow the current SDK protocol from those docs. If the docs lag behind the repo, prefer the
   real SDK contract already visible in the backend codebase.

2. Read `autonoma/discover.json` and `autonoma/scenarios.md`.
   - `discover.json` is the schema source of truth
   - `scenarios.md` is the planning layer that defines what `standard`, `empty`, and `large`
     should look like

3. Explore the backend codebase to determine:
   - whether the Autonoma SDK is already installed
   - where the Environment Factory endpoint lives
   - which parts already exist: `discover`, `up`, `down`, auth callback, teardown helpers
   - what framework and ORM patterns the backend already uses

## CRITICAL: Before Writing Any Code

Ask the user for confirmation before implementing. Present a short plan:

> "I'm about to implement or complete the Autonoma Environment Factory. Here's what I'll do:
>
> **Endpoint location**: [route / handler path]
> **Current state**: [what already exists vs what is missing]
> **Step 4 scope**: make discover/up/down work with the current SDK contract and validate the planned scenarios against it
> **Database operations**: `up` will create isolated test data and `down` will delete only those created refs
> **Security**: HMAC-SHA256 request signing with `AUTONOMA_SHARED_SECRET` plus signed refs tokens with `AUTONOMA_SIGNING_SECRET`
>
> **Environment variables needed**:
> - `AUTONOMA_SHARED_SECRET`
> - `AUTONOMA_SIGNING_SECRET`
>
> Shall I proceed?"

Do NOT proceed until the user confirms.

## Implementation Requirements

### Build on the existing backend

- Prefer extending the existing Environment Factory endpoint over replacing it
- Match the backend's framework, ORM, and route conventions
- Do not create a separate throwaway server

### Current SDK contract

Implement or preserve these actions:

| Action | Purpose |
|--------|---------|
| `discover` | Return schema metadata: version, sdk info, models, edges, relations, scopeField |
| `up` | Accept inline `create` payloads plus optional `testRunId`, create data, return `auth`, `refs`, and `refsToken` |
| `down` | Accept `refsToken`, verify it, and tear down the created data |

### Security requirements

Use these exact environment variable names:
- `AUTONOMA_SHARED_SECRET` — HMAC request verification secret shared with Autonoma
- `AUTONOMA_SIGNING_SECRET` — private secret for signing and verifying refs tokens

Required protections:
1. production guard unless explicitly allowed
2. HMAC-SHA256 verification of the `x-signature` header
3. signed refs tokens for teardown

### Scenario implementation guidance

- Use `autonoma/scenarios.md` to decide what data the backend needs to support
- Preserve generated fields as generated values; do not force everything into static literals
- Make unique fields depend on `testRunId` when needed
- Prefer explicit create and teardown ordering based on the schema
- If `discover` already works but `up` / `down` do not, keep the introspection path and finish the lifecycle

## CRITICAL: Smoke-Test and Validate Within the Session

After implementing, test the lifecycle in-session.

At minimum:
1. confirm `discover` still works
2. send one signed `up` request with a small inline `create` payload compatible with the schema
3. send the corresponding signed `down` request using the returned `refsToken`
4. verify cleanup succeeds

After the wiring works, validate `standard`, `empty`, and `large` against the backend.
Prefer:
1. backend-local `checkScenario` / `checkAllScenarios`
2. signed endpoint `up` / `down` validation if local SDK checks are not practical

Write the approved results to `autonoma/scenario-recipes.json`.

If any smoke test fails, fix the implementation and re-test.

## What to Explain to the User

When finished, explain:
1. where the Environment Factory lives in the backend
2. what was added or fixed
3. what env vars are required:
   - `AUTONOMA_SHARED_SECRET`
   - `AUTONOMA_SIGNING_SECRET`
4. what smoke tests were run and whether the lifecycle succeeded
5. whether `standard`, `empty`, and `large` validated successfully
6. where `autonoma/scenario-recipes.json` was written

## Important

- Do not remove or rewrite existing working discover logic just because Step 2 now consumes it
- Treat `discover.json` as the schema contract and `scenarios.md` as the scenario intent
- Step 4 is both Environment Factory implementation/integration and scenario validation
- Keep backend changes minimal and consistent with the repo's style
- Do not claim rollback semantics unless the backend actually implements rollback
