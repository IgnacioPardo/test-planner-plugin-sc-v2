"""Tests for validate_scenarios.py — scenarios.md frontmatter validation."""
from conftest import run_validator

SCRIPT = 'validate_scenarios.py'

VALID = """\
---
scenario_count: 3
scenarios:
  - name: standard
    description: Typical usage
    entity_types: 2
    total_entities: 10
  - name: empty
    description: No data
    entity_types: 0
    total_entities: 0
  - name: large
    description: Stress test
    entity_types: 3
    total_entities: 1000
entity_types:
  - name: user
  - name: task
discover:
  source: sdk
  model_count: 4
  edge_count: 3
  relation_count: 2
  scope_field: organizationId
variable_fields:
  - token: <project_title>
    entity: Project.title
    scenarios:
      - standard
      - large
    generator: faker.company.name
    reason: title must be unique per test run
    test_reference: (<project_title> variable)
---

# Scenarios

## SDK Discover

Models: 4

## Schema Summary

- User
- Task

## Relationship Map

- User.organizationId -> Organization.id

## Variable Data Strategy

- `<project_title>` is generated.

## Scenario: `standard`

Standard details.

## Scenario: `empty`

Empty details.

## Scenario: `large`

Large details.
"""


def test_valid_scenarios():
    code, out = run_validator(SCRIPT, VALID)
    assert code == 0
    assert out == 'OK'


def test_missing_frontmatter():
    code, out = run_validator(SCRIPT, 'no frontmatter')
    assert code == 1
    assert 'must start with YAML frontmatter' in out


def test_missing_required_fields():
    content = '---\nscenario_count: 3\n---\nbody'
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'Missing required frontmatter fields' in out


def test_missing_discover_field():
    content = VALID.replace(
        "discover:\n  source: sdk\n  model_count: 4\n  edge_count: 3\n  relation_count: 2\n  scope_field: organizationId\n",
        "",
    )
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert "discover" in out


def test_discover_source_must_be_sdk():
    content = VALID.replace('source: sdk', 'source: codebase')
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'discover.source must be exactly "sdk"' in out


def test_scenario_count_too_low():
    content = VALID.replace('scenario_count: 3', 'scenario_count: 2')
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'scenario_count must be an integer >= 3' in out


def test_scenario_count_mismatch():
    content = VALID.replace('scenario_count: 3', 'scenario_count: 5')
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'must match scenario_count' in out


def test_missing_required_scenario_name():
    content = VALID.replace('name: large', 'name: extra')
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'Missing required scenarios' in out
    assert 'large' in out


def test_scenario_missing_field():
    content = VALID.replace(
        '  - name: standard\n    description: Typical usage',
        '  - name: standard',
    )
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'missing required field: description' in out


def test_empty_entity_types():
    content = VALID.replace(
        'entity_types:\n  - name: user\n  - name: task',
        'entity_types: []',
    )
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'entity_types must be a non-empty list' in out


def test_entity_type_missing_name():
    content = VALID.replace(
        'entity_types:\n  - name: user\n  - name: task',
        'entity_types:\n  - description: no name field',
    )
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'must be a mapping with at least a "name" field' in out


def test_variable_token_must_use_angle_brackets():
    content = VALID.replace('token: <project_title>', 'token: project_title')
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'must use angle brackets' in out


def test_variable_scenarios_must_be_known():
    content = VALID.replace('      - large', '      - invalid')
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'unknown scenario names' in out


def test_missing_required_body_section():
    content = VALID.replace('## Variable Data Strategy\n\n- `<project_title>` is generated.\n\n', '')
    code, out = run_validator(SCRIPT, content)
    assert code == 1
    assert 'Missing required section in body: ## Variable Data Strategy' in out
