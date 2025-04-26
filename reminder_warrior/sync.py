"""Stub SyncManager for orchestrating sync logic."""
class SyncManager:
    """Manage synchronization state and perform sync operations."""
    def __init__(self, reminders_client=None, taskwarrior_client=None, sync_state_file=None):
        self.reminders_client = reminders_client
        self.taskwarrior_client = taskwarrior_client
        self.sync_state_file = sync_state_file

    def sync_from_reminders(self, list_name, dry_run=False, show_progress=False):
        """
        Perform sync from Apple Reminders to Taskwarrior.

        Returns a dict with keys: total, new, skipped, elapsed_seconds.
        """
        return {'total': 0, 'new': 0, 'skipped': 0, 'elapsed_seconds': 0}