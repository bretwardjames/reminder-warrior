# Reminder Warrior

[![WIP](https://img.shields.io/badge/status-WIP-yellow.svg)](https://github.com/yourusername/reminder-warrior)

This repository will be rebuilt from the ground up. Here's the high-level plan:

1. CLI with click and subcommands:
   - `list`: List available Apple Reminders lists.
   - `config`: Configure Taskwarrior UDA for storing reminder IDs.
   - `sync`: One-way sync from Apple Reminders to Taskwarrior.
2. Modular core components:
   - `reminder_warrior.apple`: Apple Reminders client.
   - `reminder_warrior.taskwarrior`: Taskwarrior client.
   - `reminder_warrior.sync`: Sync logic and state management.
3. Features:
   - Dry-run mode, verbose logging, progress bars (via `tqdm` extra).
   - Configurable sync state file path.
   - Atomic JSON state updates to avoid corruption.
4. Quality:
   - Automated tests with `pytest`.
   - Example scripts in `examples/`.
   - Comprehensive documentation.

Stay tuned for the first click-based CLI prototype!
