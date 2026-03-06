# LinuxHelpers

Useful Python3 and bash scripts for getting information such as what aliases you have registered, as well as comprehensive permission quick-reference helpers.

If you choose to use any of these scripts, it's reccomended you place them within your local `$PATH` such as `/usr/local/bin/`

## permhelp.py

Similar to `perms` except quite a bit more comprehensive as far as showcasing examples.

## catall

This tool was created prior to the release of claude-code/codex in which they had the capability to scan/understand large codebases, so I used this quick script to easily format entire directories of code, excluding what wasn't necessary such as Python bytecode stored in `__pycache__`. It simply output's all the file from the whitelist and ignores the specified exclusion list of files/directories and using the `--cl` argument, copy it to your clipboard. 

**Other args**:
- `--tree`: Print the directory tree

**Example usage**:

```bash
catall . --tree -d '.venv,.claude,__pycache_,thoughts,tests,content.pytest_cache,logos' -x CLAUDE.md,One\ Pager.pdf,uv.lock --cl
```
- Output's all files in the current directory + child directory contents except for those that are specified with `-d` for directories, and `-x` for files to exclude.


## perms

Help menu:

```bash
usage: perms [-h] [-u UMASK] [-c] [-i PATH] [--reference]
             [permissions]

Enhanced Linux Permissions & File Info Utility

positional arguments:
  permissions        Octal (e.g. 755) or symbolic (e.g. rwxr-xr-x)
                     permission

options:
  -h, --help         show this help message and exit
  -u, --umask UMASK  Explain umask (e.g. 022)
  -c, --chattr       Show chattr attributes table
  -i, --path PATH    Inspect file/directory metadata & chattr
  --reference        Show reference tables for chmod, umask, chattr
                     with examples
```

- `permissions`: [`symbolic`, `octal`] are the only two accepted arguments.


### Output examples

```bash
$ perms -i README.md    [4:08:26]

=== File/Directory Information ===
Path:       /home/supasuge/Utils/LinuxPermissionHelp/README.md
Type:       File
Size:       1148 bytes
Owner:      1000 (supasuge)
Group:      1000 (supasuge)
Accessed:   2026-03-06 04:08:26
Modified:   2026-03-06 04:08:26
Changed:    2026-03-06 04:08:26
Permissions:644 / -rw-r--r-- (User: read, write; Group: read; Others: read)
chattr flags:--------------e-------
 Attributes:
   - Extent format
```

---

```bash
$ perms -i README.md symbolic

=== Permissions Explanation ===
+--------+---------------+--------+---------+-----------+
| Type   | Permissions   | Read   | Write   | Execute   |
+========+===============+========+=========+===========+
| User   | ---           | False  | False   | False     |
+--------+---------------+--------+---------+-----------+
| Group  | ---           | False  | False   | False     |
+--------+---------------+--------+---------+-----------+
| Others | ---           | False  | False   | False     |
+--------+---------------+--------+---------+-----------+

=== Representations ===
Numeric:  000
Symbolic: ---------

=== Full Linux Permission Table ===
+---------+----------+--------------------------+
|   Octal | Symbol   | Meaning                  |
+=========+==========+==========================+
|       0 | ---      | No permission            |
+---------+----------+--------------------------+
|       1 | --x      | Execute only             |
+---------+----------+--------------------------+
|       2 | -w-      | Write only               |
+---------+----------+--------------------------+
|       3 | -wx      | Write and execute        |
+---------+----------+--------------------------+
|       4 | r--      | Read only                |
+---------+----------+--------------------------+
|       5 | r-x      | Read and execute         |
+---------+----------+--------------------------+
|       6 | rw-      | Read and write           |
+---------+----------+--------------------------+
|       7 | rwx      | Read, write, and execute |
+---------+----------+--------------------------+
```

---

```bash
$ perms -i README.md octal

=== Permissions Explanation ===
+--------+---------------+--------+---------+-----------+
| Type   | Permissions   | Read   | Write   | Execute   |
+========+===============+========+=========+===========+
| User   | ---           | False  | False   | False     |
+--------+---------------+--------+---------+-----------+
| Group  | ---           | False  | False   | False     |
+--------+---------------+--------+---------+-----------+
| Others | ---           | False  | False   | False     |
+--------+---------------+--------+---------+-----------+

=== Representations ===
Numeric:  000
Symbolic: ---------

=== Full Linux Permission Table ===
+---------+----------+--------------------------+
|   Octal | Symbol   | Meaning                  |
+=========+==========+==========================+
|       0 | ---      | No permission            |
+---------+----------+--------------------------+
|       1 | --x      | Execute only             |
+---------+----------+--------------------------+
|       2 | -w-      | Write only               |
+---------+----------+--------------------------+
|       3 | -wx      | Write and execute        |
+---------+----------+--------------------------+
|       4 | r--      | Read only                |
+---------+----------+--------------------------+
|       5 | r-x      | Read and execute         |
+---------+----------+--------------------------+
|       6 | rw-      | Read and write           |
+---------+----------+--------------------------+
|       7 | rwx      | Read, write, and execute |
+---------+----------+--------------------------+
```

---

```bash
$ perms -i README.md -c -u
usage: perms [-h] [-u UMASK] [-c] [-i PATH] [--reference]
             [permissions]
perms: error: argument -u/--umask: expected one argument
supasuge:LinuxPermissionHelp/ (main*) $ perms -i README.md -c [4:09:04]

=== File/Directory Information ===
Path:       /home/supasuge/Utils/LinuxPermissionHelp/README.md
Type:       File
Size:       1148 bytes
Owner:      1000 (supasuge)
Group:      1000 (supasuge)
Accessed:   2026-03-06 04:08:26
Modified:   2026-03-06 04:08:26
Changed:    2026-03-06 04:08:26
Permissions:644 / -rw-r--r-- (User: read, write; Group: read; Others: read)
chattr flags:--------------e-------
 Attributes:
   - Extent format
```


## chmod-calc

This tool is based off of KickSecure's built-in tool `chmod-calc` but made better with prettier output (tabular).

Help menu:

```bash
usage: chmod-calc [-h] file

chmod‑calculator – display permissions, type and attributes of a file
using a tidy tabular layout.

positional arguments:
  file        Path to the file to analyze.

options:
  -h, --help  show this help message and exit
```



