"""Tests for validate_scenario_recipes.py."""
import json
from conftest import run_validator

SCRIPT = 'validate_scenario_recipes.py'

VALID_DATA = {
    'version': 1,
    'source': {
        'discover_path': 'autonoma/discover.json',
        'scenarios_path': 'autonoma/scenarios.md',
    },
    'validation_mode': 'sdk-check',
    'recipes': [
        {
            'name': 'standard',
            'description': 'Realistic variety for core flows',
            'create': {
                'Organization': [{'name': 'Standard Org {{testRunId}}'}],
            },
            'validation': {
                'status': 'validated',
                'method': 'checkScenario',
                'phase': 'ok',
                'up_ms': 12,
                'down_ms': 8,
            },
        },
        {
            'name': 'empty',
            'description': 'Empty-state scenario',
            'create': {
                'Organization': [{'name': 'Empty Org {{testRunId}}'}],
            },
            'validation': {
                'status': 'validated',
                'method': 'checkScenario',
                'phase': 'ok',
            },
        },
        {
            'name': 'large',
            'description': 'High-volume scenario',
            'create': {
                'Organization': [{'name': 'Large Org {{testRunId}}'}],
            },
            'validation': {
                'status': 'validated',
                'method': 'endpoint-up-down',
                'phase': 'ok',
                'up_ms': 120,
                'down_ms': 65,
            },
        },
    ],
}


def _json(data):
    return json.dumps(data)


def test_valid_scenario_recipes():
    code, out = run_validator(SCRIPT, _json(VALID_DATA), 'scenario-recipes.json')
    assert code == 0
    assert out == 'OK'


def test_invalid_json():
    code, out = run_validator(SCRIPT, '{not json', 'scenario-recipes.json')
    assert code == 1
    assert 'Invalid JSON' in out


def test_missing_required_fields():
    code, out = run_validator(SCRIPT, _json({'recipes': []}), 'scenario-recipes.json')
    assert code == 1
    assert 'Missing required fields' in out


def test_invalid_validation_mode():
    data = {**VALID_DATA, 'validation_mode': 'rollback'}
    code, out = run_validator(SCRIPT, _json(data), 'scenario-recipes.json')
    assert code == 1
    assert 'validation_mode must be one of' in out


def test_missing_required_recipe_name():
    data = {**VALID_DATA}
    data['recipes'] = [
        VALID_DATA['recipes'][0],
        VALID_DATA['recipes'][1],
        {
            'name': 'custom',
            'description': 'Extra recipe',
            'create': {
                'Organization': [{'name': 'Custom Org {{testRunId}}'}],
            },
            'validation': {
                'status': 'validated',
                'method': 'checkScenario',
                'phase': 'ok',
            },
        },
    ]
    code, out = run_validator(SCRIPT, _json(data), 'scenario-recipes.json')
    assert code == 1
    assert 'Missing required recipes' in out


def test_recipe_requires_create():
    data = {**VALID_DATA}
    data['recipes'] = [dict(recipe) for recipe in VALID_DATA['recipes']]
    data['recipes'][0]['create'] = {}
    code, out = run_validator(SCRIPT, _json(data), 'scenario-recipes.json')
    assert code == 1
    assert 'create must be a non-empty object' in out


def test_validation_status_must_be_validated():
    data = {**VALID_DATA}
    data['recipes'] = [dict(recipe) for recipe in VALID_DATA['recipes']]
    data['recipes'][0]['validation'] = dict(data['recipes'][0]['validation'])
    data['recipes'][0]['validation']['status'] = 'draft'
    code, out = run_validator(SCRIPT, _json(data), 'scenario-recipes.json')
    assert code == 1
    assert 'validation.status must be exactly "validated"' in out


def test_validation_phase_must_be_ok():
    data = {**VALID_DATA}
    data['recipes'] = [dict(recipe) for recipe in VALID_DATA['recipes']]
    data['recipes'][0]['validation'] = dict(data['recipes'][0]['validation'])
    data['recipes'][0]['validation']['phase'] = 'up'
    code, out = run_validator(SCRIPT, _json(data), 'scenario-recipes.json')
    assert code == 1
    assert 'validation.phase must be exactly "ok"' in out


def test_validation_method_must_be_known():
    data = {**VALID_DATA}
    data['recipes'] = [dict(recipe) for recipe in VALID_DATA['recipes']]
    data['recipes'][0]['validation'] = dict(data['recipes'][0]['validation'])
    data['recipes'][0]['validation']['method'] = 'custom'
    code, out = run_validator(SCRIPT, _json(data), 'scenario-recipes.json')
    assert code == 1
    assert 'validation.method must be one of' in out
