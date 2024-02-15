#!/usr/bin/env python3

import click, filecmp, shutil, os, sys

EXCLUDED_FILES = [".docker_stats", ".entrypoint", ".jupyter-server-log.txt", ".stderr", ".stdout"]

@click.group()
def cli():
    pass

def compare_directories(dir1, dir2, ef):
    # Check differences between dir1 and dir2 recursively
    dcmp = filecmp.dircmp(dir1, dir2)
    dir1_files = [os.path.join(dir1, f) for f in dcmp.left_only if f not in ef]
    dir2_files = [os.path.join(dir2, f) for f in dcmp.right_only if f not in ef]
    # Recursively compare subdirectories
    for sub_dir in dcmp.common_dirs:
        sub_dir1 = os.path.join(dir1, sub_dir)
        sub_dir2 = os.path.join(dir2, sub_dir)
        sub_dir1_files, sub_dir2_files = compare_directories(sub_dir1, sub_dir2, ef)
        dir1_files.extend(sub_dir1_files)
        dir2_files.extend(sub_dir2_files)
    return dir1_files, dir2_files

def process_output(dir1, dir2):
    update, delete, add = set(), set(), set()
    
    files1 = set(dir1)
    files2 = set(dir2)
    for f in files1:
        if f in files2:
            update.add(f)
            file2.remove(f)
        else:
            delete.add(f)
    add = files2
    return update, delete, add

@cli.command()
@click.option('--trp', '-p', required=True, type=str, help='Name of the Trusted Research Performance (TRP)')
def diff(trp):
    """Check differences between pre-TRP and post-TRP"""
    # Before executing the given TRP
    dir1 = f"../runs/{trp}/version/workspace/"
    # After executing the given TRP
    dir2 = f"../runs/{trp}/workspace/"

    # Compare two directories
    out_dir1_files, out_dir2_files = compare_directories(dir1, dir2, ef=EXCLUDED_FILES)
    out_update, out_delete, out_add = process_output(out_dir1_files, out_dir2_files)
    print(f"After running {trp}:")
    if out_delete:
        print("These files were removed: ", out_delete)
    if out_add:
        print("These files were added: ", out_add)
    if out_update:
        print("These files were updated: ", out_update)

@cli.command()
@click.option('--trp', '-p', required=True, type=str, help='Name of the Trusted Research Performance (TRP)')
def sync_workspace(trp):
    """Sync the post-TRP folder to current workspace"""
    # Current working space
    dir1 = "../workspace/"
    # After executing the given TRP
    dir2 = f"../runs/{trp}/workspace/"

    # Compare two directories
    out_dir1_files, out_dir2_files = compare_directories(dir1, dir2, ef=EXCLUDED_FILES)
    out_update, out_delete, out_add = process_output(out_dir1_files, out_dir2_files)
    # Combine out_update and out_add
    out_update.update(out_add)
    for f in out_update:
        shutil.copy(f, f.replace(f"runs/{trp}/", ""))

if __name__ == '__main__':
    cli()
