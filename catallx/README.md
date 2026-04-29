# catallx

`catallx` walks a directory, filters files by extension or path rules, and emits a
copy-friendly bundle of the directory tree plus file contents. Output can be
Markdown or XML, and the optional tree view uses ANSI colors grouped by file
families so related extensions are easy to scan.

![alt text](image.png)

```
(catallx) supasuge@scr3wy:~/Utils/LinuxHelpers|main⚡ ⇒  catallx . -i
# Directory Structure
├── 📘 README.md
└── 📁 Scripts
    ├── 📁 Install-VirtMan
    │   └── 💻 install-virtman.sh
    └── 💻 install-docker-ubuntu.sh
```

**Output**

```

# File Contents (Markdown Format)

## README.md

```md
# LinuxHelpers

Useful Python3 and bash scripts for getting information such as what aliases you have registered, as well as comprehensive permission quick-reference helpers.

If you choose to use any of these scripts, it's reccomended you place them within your local `$PATH` such as `/usr/local/bin/`

## permhelp.py

Similar to `perms` except quite a bit more comprehensive as far as showcasing examples.

## perms

Help menu:

\`\`\`bash
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
\`\`\`

- `permissions`: [`symbolic`, `octal`] are the only two accepted arguments.


### Output examples

\`\`\`bash
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
\`\`\`

---

\`\`\`bash
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
\`\`\`

---

\`\`\`bash
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
\`\`\`

---

\`\`\`bash
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
\`\`\`


## chmod-calc

This tool is based off of KickSecure's built-in tool `chmod-calc` but made better with prettier output (tabular).

Help menu:

\`\`\`bash
usage: chmod-calc [-h] file

chmod‑calculator – display permissions, type and attributes of a file
using a tidy tabular layout.

positional arguments:
  file        Path to the file to analyze.

options:
  -h, --help  show this help message and exit
\`\`\`




\`\`\`

## Scripts/install-docker-ubuntu.sh

\`\`\`sh
#!/bin/bash
set -euo pipefail

if [[ "$EUID" = 0 ]]; then
    echo "(1) already root"
else
    sudo -k # make sure to ask for password on next sudo ✱
    if sudo true; then
        echo "(2) correct password"
    else
        echo "(3) wrong password"
        exit 1
    fi
fi
# Do your sudo stuff here. Password will not be asked again due to caching.

ARCHITECTURE=$(dpkg --print-architecture)

sudo apt update -y
sudo apt upgrade -y
echo "Finished update + upgradek, installing (ca-certificates, curl, gnupg)"
sudo apt install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo "Adding docker.source to apt list"
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: ${ARCHITECTURE}
Signed-By: /etc/apt/keyrings/docker.asc
EOF
echo "Done... Installing docker engine and adding current user to group"
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl start docker
docker run hello world

\`\`\`
```

## Features

- Markdown or XML output for use with editors, LLM prompts, notes, and audits.
- Colored directory trees with similar colors for folders and related file types.
- Extension-aware filtering with a broad default allow list for source, config,
  shell, docs, data, image, and build files.
- Default ignores for noisy folders such as `.git`, `node_modules`, `__pycache__`,
  `.venv`, `dist`, and `build`.
- Textual-powered interactive selector for excluding individual files or folders.
- Clipboard copy support through `xclip`, `wl-copy`, or `pbcopy`.

## Installation with uv

Install directly from this project directory:

```bash
uv tool install .
```

After installing, run:

```bash
catallx --help
```

For local development, create and sync the project environment:

```bash
uv sync
```

Run the CLI without installing it globally:

```bash
uv run catallx --help
uv run catallx src --tree
```

If you make changes and want the globally installed command to pick them up
immediately, reinstall it:

```bash
uv tool install --force .
```

## Basic Usage

Show the help menu:

```bash
catallx --help
```

Dump a directory as Markdown:

```bash
catallx /path/to/project
```

Include a colored tree before the file contents:

```bash
catallx /path/to/project --tree
```

Emit XML instead of Markdown:

```bash
catallx /path/to/project --format xml
```

Disable ANSI color in the tree:

```bash
catallx /path/to/project --tree --no-color
```

Copy the generated output to your clipboard:

```bash
catallx /path/to/project --tree --cl
```

Running `catallx` with no arguments prints the help menu. The directory argument
is validated before scanning; missing paths and file paths are rejected with a
clear error.

## Filtering

Exclude extensions, filenames, or subtrees:

```bash
catallx . --exclude pyc,package-lock.json,generated/*
```

Exclude directory names wherever they appear:

```bash
catallx . --exclude-dirs env,coverage,tmp
```

Only include selected extensions or glob patterns:

```bash
catallx . --only py,md,toml
catallx . --only "*.py,src/**/*.md"
```

Disable the built-in directory blacklist:

```bash
catallx . --no-default-blacklist
```

Use the interactive selector to choose exclusions before generating output:

```bash
catallx . --interactive # same as -i
```

Interactive controls:

- `Up` / `Down`: move through visible files and folders.
- `Enter`: expand or collapse a folder.
- `Space`: toggle an exclusion.
- `g`: generate output.
- `q`: quit without generating output.

The interactive selector runs as a full-screen Textual terminal UI and uses the
same file-family colors as the generated tree.

## Output Notes

Image and binary-like formats such as `png`, `jpg`, `gif`, `webp`, `svg`, and
`pdf` are listed but their contents are not embedded. Text files that are not
valid UTF-8 are also reported instead of crashing the command.

The colored tree groups related extensions with similar styles:

- Folders use blue.
- Python uses green.
- JavaScript and TypeScript use yellow/blue.
- Web assets use bright magenta.
- Config and structured metadata use cyan/yellow.
- Shell scripts use green.
- System languages such as C, C++, Rust, Objective-C, and Zig use bright cyan.
- JVM and .NET languages use warm magenta/red tones.

## Examples

Prepare a compact prompt bundle for a Python package:

```bash
catallx . --tree --only py,toml,md --exclude-dirs .cache
```

Review only configuration and documentation:

```bash
catallx . --tree --only json,yaml,yml,toml,md
```

Create XML for another tool and copy it to the clipboard:

```bash
catallx . --format xml --cl
```
