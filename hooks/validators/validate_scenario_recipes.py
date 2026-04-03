#!/usr/bin/env python3
"""Validates autonoma/scenario-recipes.json schema."""
import json
import sys

filepath = sys.argv[1]

try:
    data = json.load(open(filepath))
except Exception as e:
    print(f'Invalid JSON: {e}')
    sys.exit(1)

if not isinstance(data, dict):
    print('Root must be a JSON object')
    sys.exit(1)

required = ['version', 'source', 'validationMode', 'recipes']
missing = [f for f in required if f not in data]
if missing:
    print(f'Missing required fields: {missing}')
    sys.exit(1)

version = data.get('version')
if version != 1:
    print('version must be exactly 1')
    sys.exit(1)

source = data.get('source')
if not isinstance(source, dict):
    print('source must be an object')
    sys.exit(1)

for field in ['discoverPath', 'scenariosPath']:
    value = source.get(field)
    if not isinstance(value, str) or len(value.strip()) == 0:
        print(f'source.{field} must be a non-empty string')
        sys.exit(1)

validation_mode = data.get('validationMode')
valid_modes = {'sdk-check', 'endpoint-lifecycle'}
if validation_mode not in valid_modes:
    print(f'validationMode must be one of {valid_modes}, got: {validation_mode}')
    sys.exit(1)

recipes = data.get('recipes')
if not isinstance(recipes, list) or len(recipes) < 3:
    print('recipes must be an array with at least 3 entries')
    sys.exit(1)

required_names = {'standard', 'empty', 'large'}
found_names = set()

for i, recipe in enumerate(recipes):
    if not isinstance(recipe, dict):
        print(f'recipes[{i}] must be an object')
        sys.exit(1)

    for field in ['name', 'description', 'create', 'validation']:
        if field not in recipe:
            print(f'recipes[{i}] missing required field: {field}')
            sys.exit(1)

    name = recipe.get('name')
    if not isinstance(name, str) or len(name.strip()) == 0:
        print(f'recipes[{i}].name must be a non-empty string')
        sys.exit(1)
    found_names.add(name)

    description = recipe.get('description')
    if not isinstance(description, str) or len(description.strip()) == 0:
        print(f'recipes[{i}].description must be a non-empty string')
        sys.exit(1)

    create = recipe.get('create')
    if not isinstance(create, dict) or len(create) == 0:
        print(f'recipes[{i}].create must be a non-empty object')
        sys.exit(1)

    validation = recipe.get('validation')
    if not isinstance(validation, dict):
        print(f'recipes[{i}].validation must be an object')
        sys.exit(1)

    for field in ['status', 'method', 'phase']:
        if field not in validation:
            print(f'recipes[{i}].validation missing required field: {field}')
            sys.exit(1)

    if validation.get('status') != 'validated':
        print(f'recipes[{i}].validation.status must be exactly "validated"')
        sys.exit(1)

    if validation.get('phase') != 'ok':
        print(f'recipes[{i}].validation.phase must be exactly "ok"')
        sys.exit(1)

    method = validation.get('method')
    valid_methods = {'checkScenario', 'checkAllScenarios', 'endpoint-up-down'}
    if method not in valid_methods:
        print(f'recipes[{i}].validation.method must be one of {valid_methods}, got: {method}')
        sys.exit(1)

    for field in ['up_ms', 'down_ms']:
        if field in validation:
            value = validation.get(field)
            if not isinstance(value, int) or value < 0:
                print(f'recipes[{i}].validation.{field} must be a non-negative integer')
                sys.exit(1)

missing_names = required_names - found_names
if missing_names:
    print(f'Missing required recipes: {missing_names}')
    sys.exit(1)

print('OK')
