"""Stub Apple Reminders client to be implemented."""
class AppleRemindersClient:
    """Interact with Apple Reminders via EventKit or AppleScript."""
    def get_lists(self):
        """Return a list of available reminders list names."""
        import subprocess
        import re

        script = 'tell application "Reminders" to get name of lists'
        import subprocess
        try:
            proc = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, check=True,
                timeout=5
            )
        except FileNotFoundError:
            raise RuntimeError("`osascript` not found; Apple Reminders client requires macOS")
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "`osascript` timed out. Please grant Terminal Automation access to Reminders."
            )
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() or str(e)
            raise RuntimeError(f"Failed to list Apple Reminders lists: {err}")

        output = proc.stdout.strip()
        if not output:
            return []
        # AppleScript returns comma-separated names; handle newlines as well
        items = re.split(r',\s*|[\r\n]+', output)
        return [name.strip() for name in items if name.strip()]

    def get_reminders(self, list_name):
        """Return a list of reminders (dicts) from the specified list."""
        import subprocess

        # Build AppleScript to extract reminder properties
        script = f'''
tell application "Reminders"
    -- only incomplete reminders (skip completed or past occurrences)
    set rems to reminders of list "{list_name}" whose completed is false
    set output to ""
    repeat with r in rems
        set rId to id of r
        set rName to name of r
        set rBody to body of r
        if due date of r is missing value then
            set rDue to ""
        else
            set rDue to due date of r as string
        end if
        set output to output & rId & "||" & rName & "||" & rBody & "||" & rDue & "\n"
    end repeat
    return output
end tell
'''
        # Execute the script via a temporary AppleScript file
        import tempfile, os, subprocess
        fname = None
        try:
            # Write script to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.applescript', delete=False) as tf:
                tf.write(script)
                fname = tf.name
            # Execute with timeout to avoid hanging on permission dialogs
            proc = subprocess.run([
                "osascript", fname
            ], capture_output=True, text=True, check=True, timeout=5)
        except FileNotFoundError:
            raise RuntimeError("`osascript` not found; Apple Reminders client requires macOS")
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "`osascript` timed out. Please grant Terminal (or your shell) Automation access to Reminders in System Settings."
            )
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() or str(e)
            raise RuntimeError(f"Failed to fetch reminders: {err}")
        finally:
            if fname:
                try:
                    os.remove(fname)
                except OSError:
                    pass
        output = proc.stdout or ''
        reminders = []
        for line in output.splitlines():
            parts = line.split('||')
            if len(parts) != 4:
                continue
            r_id, title, notes, due = parts
            item = {'id': r_id, 'title': title, 'notes': notes}
            if due:
                item['due'] = due
            reminders.append(item)
        return reminders
    
    def get_all_reminders(self):
        """Return a dict mapping each list name to its reminders list."""
        import subprocess, tempfile, os

        script = '''
tell application "Reminders"
    set output to ""
    repeat with l in lists
        set listName to name of l
        set rems to reminders of l whose completed is false
        repeat with r in rems
            set rId to id of r
            set rName to name of r
            set rBody to body of r
            if due date of r is missing value then
                set rDue to ""
            else
                set rDue to due date of r as string
            end if
            set output to output & listName & "||" & rId & "||" & rName & "||" & rBody & "||" & rDue & "\n"
        end repeat
    end repeat
    return output
end tell
'''
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.applescript', delete=False) as tf:
            tf.write(script)
            fname = tf.name
        try:
            proc = subprocess.run([
                "osascript", fname
            ], capture_output=True, text=True, check=True)
        except FileNotFoundError:
            raise RuntimeError("`osascript` not found; Apple Reminders client requires macOS")
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() or str(e)
            raise RuntimeError(f"Failed to fetch all reminders: {err}")
        finally:
            try:
                os.remove(fname)
            except Exception:
                pass
        # Parse output
        data = {}
        for line in (proc.stdout or '').splitlines():
            parts = line.split('||')
            if len(parts) != 5:
                continue
            lst, r_id, title, notes, due = parts
            item = {'id': r_id, 'title': title, 'notes': notes}
            if due:
                item['due'] = due
            data.setdefault(lst, []).append(item)
        return data