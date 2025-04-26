import sys
import logging
import click

from .apple_reminders import AppleRemindersClient
from .taskwarrior import TaskwarriorClient
from .sync import SyncManager
from .config import load_config, save_config

@click.group()
@click.version_option()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--sync-state-file', default='~/.reminder_warrior_sync.json',
              help='Path to the sync state file')
@click.pass_context
def cli(ctx, verbose, sync_state_file):
    """
    Reminder Warrior CLI: sync tasks between Apple Reminders and Taskwarrior.
    """
    lvl = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=lvl,
        format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    ctx.obj = {
        'verbose': verbose,
        'sync_state_file': sync_state_file
    }

@cli.command()
@click.option('--list', 'list_name', default=None,
              help='Apple Reminders list to sync from (overrides default)')
@click.option('--dry-run', '-n', is_flag=True, help='Dry run (no writes)')
@click.option('--progress', is_flag=True, help='Show progress bars (tqdm)')
@click.pass_context
def sync(ctx, list_name, dry_run, progress):
    """Sync tasks from Apple Reminders into Taskwarrior."""
    reminders = AppleRemindersClient()
    tw = TaskwarriorClient()
    mgr = SyncManager(
        reminders_client=reminders,
        taskwarrior_client=tw,
        sync_state_file=ctx.obj['sync_state_file']
    )
    # Determine which list(s) to sync
    if list_name:
        lists = [list_name]
    else:
        cfg = load_config()
        default = cfg.get('default_list')
        if not default:
            click.echo(
                "No reminders list specified. Use --list or run `reminder-warrior set-list` to configure a default.",
                err=True
            )
            sys.exit(1)
        if default == '*':
            lists = reminders.get_lists()
        else:
            lists = [default]
    overall = {'total': 0, 'new': 0, 'skipped': 0}
    for lst in lists:
        try:
            stats = mgr.sync_from_reminders(
                list_name=lst,
                dry_run=dry_run,
                show_progress=progress
            )
            click.echo(
                f"[{lst}] Done: total={stats['total']} new={stats['new']} "
                f"skipped={stats['skipped']} time={stats['elapsed_seconds']:.2f}s"
            )
            overall['total'] += stats['total']
            overall['new'] += stats['new']
            overall['skipped'] += stats['skipped']
        except Exception as err:
            click.echo(f"⚠️  Sync failed for list '{lst}': {err}", err=True)
    click.echo(
        f"Overall: total={overall['total']} new={overall['new']} skipped={overall['skipped']}"
    )

@cli.command('list')
@click.pass_context
def list_lists(ctx):
    """List all available Apple Reminders lists."""
    try:
        for name in AppleRemindersClient().get_lists():
            click.echo(name)
    except Exception as err:
        click.echo(f"⚠️  Error: {err}", err=True)
        sys.exit(1)
    
@cli.command('set-list')
@click.pass_context
def set_list(ctx):
    """Configure the default Apple Reminders list to sync."""
    client = AppleRemindersClient()
    try:
        lists = client.get_lists()
    except Exception as err:
        click.echo(f"Error fetching lists: {err}", err=True)
        sys.exit(1)
    if not lists:
        click.echo("No Reminders lists available.", err=True)
        sys.exit(1)
    click.echo("0. All lists")
    for idx, name in enumerate(lists, start=1):
        click.echo(f"{idx}. {name}")
    choice = click.prompt("Select default list (0=All, number)", type=int, default=0)
    if choice == 0:
        selected = '*'
    elif 1 <= choice <= len(lists):
        selected = lists[choice - 1]
    else:
        click.echo("Invalid selection.", err=True)
        sys.exit(1)
    cfg = load_config()
    cfg['default_list'] = selected
    save_config(cfg)
    click.echo(f"Default Reminders list set to: '{selected}'")
    
@cli.command('reminders')
@click.option('--list', 'list_name', default=None,
              help='Apple Reminders list to show reminders from (overrides default)')
@click.pass_context
def list_reminders(ctx, list_name):
    """List reminders in an Apple Reminders list."""
    client = AppleRemindersClient()
    # Determine which list(s) to show
    if list_name:
        lists = [list_name]
        fetch_all = False
    else:
        cfg = load_config()
        default = cfg.get('default_list')
        if not default:
            click.echo(
                "No reminders list specified. Use --list or run `reminder-warrior set-list` to configure a default.",
                err=True
            )
            sys.exit(1)
        if default == '*':
            fetch_all = True
        else:
            lists = [default]
            fetch_all = False
    # If user wants all lists, fetch once in bulk
    if fetch_all:
        try:
            all_rems = client.get_all_reminders()
        except Exception as err:
            click.echo(f"Error fetching all reminders: {err}", err=True)
            sys.exit(1)
        for lst, rems in all_rems.items():
            click.echo(f"== {lst} ==")
            if not rems:
                click.echo("(no reminders)")
                continue
            for r in rems:
                line = f"{r.get('id')}: {r.get('title')}"
                due = r.get('due')
                if due:
                    line += f" (due: {due})"
                click.echo(line)
        return
    # Otherwise, fetch per-list
    for lst in lists:
        click.echo(f"== {lst} ==")
        try:
            rems = client.get_reminders(lst)
        except Exception as err:
            click.echo(f"Error fetching reminders for '{lst}': {err}", err=True)
            continue
        if not rems:
            click.echo("(no reminders)")
            continue
        for r in rems:
            line = f"{r.get('id')}: {r.get('title')}"
            due = r.get('due')
            if due:
                line += f" (due: {due})"
            click.echo(line)

@cli.command()
@click.option('--dry-run', '-n', is_flag=True, help='Dry run configuring UDA')
@click.pass_context
def config(ctx, dry_run):  # noqa: A002
    """Configure Taskwarrior UDA for storing Apple Reminder IDs."""
    ok = TaskwarriorClient().configure_uda(dry_run=dry_run)
    if ok:
        click.echo("✅  UDA configured.")
    else:
        click.echo("❌  UDA configuration failed.", err=True)
        sys.exit(1)

def main():
    cli()

if __name__ == '__main__':
    main()