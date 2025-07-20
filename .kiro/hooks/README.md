# Kiro Agent Hooks

This directory contains agent hooks for automating tasks in the development workflow.

## Available Hooks

### Pre-Commit Check

**File:** `pre-commit-check.json`

**Description:** This hook runs `pre-commit run --all-files` before completing any task to ensure code quality standards are met.

**Trigger:** Executes when a task is about to be completed.

**Behavior:**

- Runs all pre-commit checks on all files
- Blocks task completion if any checks fail
- Provides feedback on success or failure

**Usage:**
When you complete a task in any spec, this hook will automatically run the pre-commit checks to ensure code quality before marking the task as complete.

## Adding New Hooks

To add a new hook:

1. Create a new JSON file in this directory
2. Define the trigger, action, and options
3. Document the hook in this README
