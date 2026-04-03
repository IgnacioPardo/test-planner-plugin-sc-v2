# Autonoma Test Planner

A Claude Code plugin that generates comprehensive E2E test suites for your codebase through a validated 4-step pipeline.

Each step runs in an isolated subagent with deterministic validation — shell scripts check the output format before the pipeline advances. No hallucinated validations, no cascading errors.

## Install

**Step 1:** Add the marketplace:

```
/plugin marketplace add Autonoma-AI/test-planner-plugin
```

**Step 2:** Install the plugin:

```
/plugin install autonoma-test-planner@autonoma
```

## Usage

Inside any project with Claude Code:

```
/autonoma-test-planner:generate-tests
```

The plugin walks you through 4 steps, asking for confirmation at each checkpoint before proceeding.

## How it works

### Step 1: Knowledge Base

Analyzes your frontend codebase and produces `autonoma/AUTONOMA.md` — a user-perspective map of every page, flow, and feature. The file includes YAML frontmatter with a core flows table that determines how test coverage is distributed.

**You review**: the core flows table. If a flow is marked `core: true`, it gets 50-60% of test coverage.

### Step 2: Scenarios

Reads the knowledge base and the SDK `discover` response from your backend Environment Factory to design three test data environments: `standard` (realistic variety), `empty` (empty states), and `large` (pagination/performance). Outputs `autonoma/discover.json` plus `autonoma/scenarios.md`, preserving the legacy scenario summary while adding schema metadata and variable-field planning.

**You review**: entity names, counts, relationships, and which values must stay generated. Fixed values become hard assertions; variable fields are explicitly marked for later test generation.

### Step 3: E2E Tests

Generates markdown test files organized by feature in `autonoma/qa-tests/`. Each test has frontmatter (title, description, criticality, scenario, flow) and uses only natural-language steps: click, scroll, type, assert.

An `INDEX.md` tracks total test count, folder breakdown, and coverage correlation with your codebase size.

`scenarios.md` is fixture input for this step, not the subject under test. Step 3 should not spend test budget verifying seeded counts or Environment Factory correctness.

**You review**: test distribution and coverage correlation. Test count should roughly match 3-5x your route/feature count.

### Step 4: Environment Factory

Implements or completes the backend Environment Factory so the planned scenarios can actually be created and torn down through the current SDK contract. Step 4 includes backend wiring plus validation: `discover`, `up`, `down`, request signing, refs signing, a smoke-tested lifecycle, and validation of the planned scenarios with `autonoma/scenario-recipes.json`.

**You review**: where the Environment Factory lives, what changed, whether a smoke `discover` → `up` → `down` check passed, and whether `standard`, `empty`, and `large` all passed lifecycle validation.

## Validation

Every output file has YAML frontmatter validated by shell scripts (not prompts). If validation fails, Claude sees the error and must fix it before proceeding.

| File | What's validated |
|------|-----------------|
| `AUTONOMA.md` | core_flows table, app description, feature/skill counts |
| `discover.json` | SDK discover schema shape: models, edges, relations, scopeField |
| `scenarios.md` | scenario count, required scenarios (standard/empty/large), entity types, discover metadata, variable fields |
| `scenario-recipes.json` | validated recipe file, lifecycle method, required scenarios |
| `INDEX.md` | test totals match folder sums, criticality counts sum correctly, test count within expected range |
| Each test file | title, description, criticality (critical/high/mid/low), scenario, flow |

## Environment Variables

Step 2 and Step 4 use the live SDK endpoint when fetching `discover` or validating through HTTP:

```bash
AUTONOMA_SDK_ENDPOINT=<your sdk endpoint url>
AUTONOMA_SHARED_SECRET=<shared HMAC secret>
```

Step 4 backend implementation uses the current SDK secret names:

```bash
AUTONOMA_SHARED_SECRET=<shared HMAC secret>
AUTONOMA_SIGNING_SECRET=<private refs signing secret>
```

## Requirements

- Claude Code
- Python 3 (ships with macOS/Linux)
- PyYAML (auto-installed if missing)

## Local Development

```bash
# Test locally without installing
claude --plugin-dir ./

# Validate plugin structure
claude plugin validate ./
```

## Project Structure

```
autonoma-test-planner/
├── .claude-plugin/
│   ├── plugin.json                     # Plugin manifest
│   └── marketplace.json                # Marketplace catalog
├── skills/generate-tests/SKILL.md      # /generate-tests orchestrator
├── agents/
│   ├── kb-generator.md                 # Step 1 subagent
│   ├── scenario-generator.md           # Step 2 subagent
│   ├── test-case-generator.md          # Step 3 subagent
│   └── env-factory-generator.md        # Step 4 subagent
├── hooks/
│   ├── hooks.json                      # PostToolUse hook config
│   ├── validate-pipeline-output.sh     # Validation dispatcher
│   └── validators/
│       ├── validate_kb.py
│       ├── validate_discover.py
│       ├── validate_scenario_recipes.py
│       ├── validate_scenarios.py
│       ├── validate_test_index.py
│       └── validate_test_file.py
├── LICENSE
└── README.md
```

## Documentation

Full prompt documentation: [docs.agent.autonoma.app/llms.txt](https://docs.agent.autonoma.app/llms.txt)

## License

MIT
