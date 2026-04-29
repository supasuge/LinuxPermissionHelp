#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import io
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional, Set
from xml.dom import minidom

from rich.console import Console
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static, Tree as TextualTree


WHITELIST_EXTS = {
    "1", "adoc", "ahk", "astro", "awk", "bash", "bat", "bats", "bicep", "bta",
    "c", "cc", "cfg", "clj", "cljs", "cmake", "cmd", "conf", "cpp", "cr",
    "cron", "crontab", "cs", "csh", "css", "csv", "cue", "cxx", "dart",
    "diff", "dockerfile", "dotenv", "editorconfig", "env", "erb", "erl", "ex",
    "exs", "fish", "flag", "fs", "fsi", "fsx", "gemspec", "gif", "go", "gradle",
    "graphql", "groovy", "h", "haml", "hcl", "heic", "heif", "hh", "hpp", "hs",
    "htm", "html", "http", "hxx", "ini", "ipynb", "java", "jpeg", "jpg", "js",
    "json", "json5", "jsonc", "jsx", "just", "ksh", "kt", "kts", "less", "lhs",
    "lock", "log", "lua", "m", "make", "markdown", "md", "mdx", "mjs", "mk",
    "mkd", "ml", "mli", "mm", "nim", "nix", "patch", "pbtxt", "pdf", "php",
    "pl", "pm", "png", "pod", "prisma", "properties", "proxy", "ps1", "psm1",
    "py", "pyi", "r", "rake", "rb", "rego", "resx", "rlib", "rmd", "rs", "rst",
    "ruby", "sage", "sass", "scala", "scss", "sed", "sh", "sql", "sqlite",
    "svelte", "swift", "svg", "toml", "ts", "tsx", "txt", "vue", "webp", "xml",
    "xsd", "xsl", "yaml", "yml", "zig", "zsh",
}

DEFAULT_BLACKLIST_DIRS = {
    ".cache",
    ".cursor",
    ".codex",
    "__pycache__",
    "node_modules",
    ".git",
    ".vscode",
    ".idea",
    "migrations",
    ".env",
    ".venv",
    "venv",
    "env",
    ".claude",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
}

IMAGE_EXTS = {"gif", "heic", "heif", "jpeg", "jpg", "pdf", "png", "svg", "webp"}
TEXT_EXTS = {"1", "adoc", "csv", "log", "markdown", "md", "mdx", "mkd", "pod", "rmd", "rst", "txt"}
CONFIG_EXTS = {
    "cfg", "conf", "cue", "dotenv", "editorconfig", "env", "hcl", "ini", "json",
    "json5", "jsonc", "lock", "pbtxt", "properties", "resx", "toml", "xml",
    "xsd", "xsl", "yaml", "yml",
}
SHELL_EXTS = {"ahk", "awk", "bash", "bat", "bats", "cmd", "cron", "crontab", "csh", "fish", "ksh", "ps1", "psm1", "sed", "sh", "zsh"}
WEB_EXTS = {"astro", "css", "erb", "haml", "htm", "html", "less", "sass", "scss", "svelte", "vue"}
SYSTEM_EXTS = {"c", "cc", "cpp", "cxx", "h", "hh", "hpp", "hxx", "m", "mm", "rs", "zig"}
JVM_EXTS = {"clj", "cljs", "gradle", "groovy", "java", "kt", "kts", "scala"}
DOTNET_EXTS = {"cs", "fs", "fsi", "fsx"}
DATA_EXTS = {"graphql", "http", "ipynb", "prisma", "sqlite", "sql"}
CODE_EXTS = WHITELIST_EXTS - IMAGE_EXTS - TEXT_EXTS - CONFIG_EXTS


class AnsiStyle(Enum):
    RESET = ("\x1b[0m", "none")
    BOLD = ("\x1b[1m", "bold")
    DIM = ("\x1b[2m", "dim")
    RED = ("\x1b[31m", "red")
    BOLD_RED = ("\x1b[1;31m", "bold red")
    GREEN = ("\x1b[32m", "green")
    BOLD_GREEN = ("\x1b[1;32m", "bold green")
    YELLOW = ("\x1b[33m", "yellow")
    BOLD_YELLOW = ("\x1b[1;33m", "bold yellow")
    BLUE = ("\x1b[34m", "blue")
    BOLD_BLUE = ("\x1b[1;34m", "bold blue")
    MAGENTA = ("\x1b[35m", "magenta")
    BOLD_MAGENTA = ("\x1b[1;35m", "bold magenta")
    CYAN = ("\x1b[36m", "cyan")
    BOLD_CYAN = ("\x1b[1;36m", "bold cyan")
    WHITE = ("\x1b[37m", "white")
    BRIGHT_BLACK = ("\x1b[90m", "bright_black")
    BRIGHT_RED = ("\x1b[91m", "bright_red")
    BRIGHT_GREEN = ("\x1b[92m", "bright_green")
    BRIGHT_YELLOW = ("\x1b[93m", "bright_yellow")
    BRIGHT_BLUE = ("\x1b[94m", "bright_blue")
    BRIGHT_MAGENTA = ("\x1b[95m", "bright_magenta")
    BRIGHT_CYAN = ("\x1b[96m", "bright_cyan")
    BRIGHT_WHITE = ("\x1b[97m", "bright_white")

    @property
    def ansi(self) -> str:
        return self.value[0]

    @property
    def rich(self) -> str:
        return self.value[1]


ICON_STYLE = {
    "dir": ("📁", AnsiStyle.BOLD_BLUE),
    "python": ("🐍", AnsiStyle.BOLD_GREEN),
    "javascript": ("🟨", AnsiStyle.YELLOW),
    "typescript": ("🔷", AnsiStyle.BLUE),
    "web": ("🌐", AnsiStyle.BRIGHT_MAGENTA),
    "markdown": ("📘", AnsiStyle.CYAN),
    "text": ("📄", AnsiStyle.WHITE),
    "data": ("🗄️", AnsiStyle.BOLD_YELLOW),
    "json": ("🧾", AnsiStyle.YELLOW),
    "config": ("🔧", AnsiStyle.CYAN),
    "shell": ("💻", AnsiStyle.GREEN),
    "docker": ("🐳", AnsiStyle.BLUE),
    "image": ("🖼️", AnsiStyle.MAGENTA),
    "system": ("⚙️", AnsiStyle.BRIGHT_CYAN),
    "jvm": ("☕", AnsiStyle.BRIGHT_RED),
    "dotnet": ("⬢", AnsiStyle.BRIGHT_MAGENTA),
    "go": ("Go", AnsiStyle.BRIGHT_CYAN),
    "ruby": ("◆", AnsiStyle.RED),
    "php": ("🐘", AnsiStyle.BRIGHT_BLUE),
    "code": ("⚙️", AnsiStyle.BRIGHT_CYAN),
    "default": ("📦", AnsiStyle.WHITE),
}


def get_file_extension(filename: str) -> str:
    base = os.path.basename(filename)
    _, ext = os.path.splitext(base)

    if ext:
        return ext[1:].lower()

    low = base.lower()
    return low if low in WHITELIST_EXTS else ""


def classify_path(path: str, is_dir: bool = False) -> str:
    if is_dir:
        return "dir"

    name = os.path.basename(path).lower()
    ext = get_file_extension(path)

    if name in {"dockerfile", "compose.yml", "docker-compose.yml"} or ext == "dockerfile":
        return "docker"

    if ext in {"py", "pyi", "sage"}:
        return "python"
    if ext in {"js", "jsx", "mjs"}:
        return "javascript"
    if ext in {"ts", "tsx"}:
        return "typescript"
    if ext in WEB_EXTS:
        return "web"
    if ext in {"md", "markdown", "mdx", "mkd", "rmd", "adoc", "rst"}:
        return "markdown"
    if ext in TEXT_EXTS:
        return "text"
    if ext in {"json", "json5", "jsonc"}:
        return "json"
    if ext in CONFIG_EXTS:
        return "config"
    if ext in SHELL_EXTS:
        return "shell"
    if ext in IMAGE_EXTS:
        return "image"
    if ext in SYSTEM_EXTS:
        return "system"
    if ext in JVM_EXTS:
        return "jvm"
    if ext in DOTNET_EXTS:
        return "dotnet"
    if ext == "go":
        return "go"
    if ext in {"rb", "ruby", "rake", "gemspec"}:
        return "ruby"
    if ext == "php":
        return "php"
    if ext in DATA_EXTS:
        return "data"
    if ext in CODE_EXTS:
        return "code"

    return "default"


def icon_for(path: str, is_dir: bool = False) -> tuple[str, AnsiStyle]:
    return ICON_STYLE.get(classify_path(path, is_dir), ICON_STYLE["default"])


def ansi_wrap(text: str, style: AnsiStyle, enabled: bool = True) -> str:
    if not enabled:
        return text
    return f"{style.ansi}{text}{AnsiStyle.RESET.ansi}"


def normalize_ext_token(token: str) -> str:
    token = token.strip().lower()

    if token.startswith("*."):
        token = token[2:]
    if token.startswith("."):
        token = token[1:]

    return token


def split_csv(csv: Optional[str]) -> list[str]:
    if not csv:
        return []
    return [x.strip() for x in csv.split(",") if x.strip()]


@dataclass
class Exclusions:
    base_dir: str
    use_default_blacklist: bool = True
    dirnames: Set[str] = field(default_factory=set)
    dirpaths: Set[str] = field(default_factory=set)
    filenames: Set[str] = field(default_factory=set)
    exclude_exts: Set[str] = field(default_factory=set)
    only_exts: Set[str] = field(default_factory=set)
    only_patterns: Set[str] = field(default_factory=set)

    def add_dirnames(self, csv: Optional[str]) -> None:
        for tok in split_csv(csv):
            self.dirnames.add(tok.rstrip("/"))

    def add_only_csv(self, csv: Optional[str]) -> None:
        for tok in split_csv(csv):
            low = tok.lower()

            if "*" in tok or "?" in tok:
                self.only_patterns.add(tok)
                ext = normalize_ext_token(tok)
                if ext and "*" not in ext and "?" not in ext:
                    self.only_exts.add(ext)
                continue

            ext = normalize_ext_token(tok)
            if ext in WHITELIST_EXTS:
                self.only_exts.add(ext)
            else:
                self.only_patterns.add(tok)

    def add_generic_csv(self, csv: Optional[str]) -> None:
        for tok in split_csv(csv):
            self.add_generic_token(tok)

    def add_generic_token(self, token: str) -> None:
        t = token.strip()
        if not t:
            return

        if t.endswith("/*"):
            rel = t[:-2].strip().strip(os.sep)
            if rel:
                self.dirpaths.add(os.path.normpath(os.path.join(self.base_dir, rel)))
            return

        if os.sep in t:
            self.dirpaths.add(os.path.normpath(os.path.join(self.base_dir, t)))
            return

        low = t.lower()
        ext = normalize_ext_token(low)

        if low.startswith(".") or low.startswith("*.") or ext in WHITELIST_EXTS:
            self.exclude_exts.add(ext)
            return

        if "." in low:
            self.filenames.add(low)
            return

        self.exclude_exts.add(low)

    def is_blacklisted_dirname(self, name: str) -> bool:
        return self.use_default_blacklist and name.rstrip("/") in DEFAULT_BLACKLIST_DIRS

    def exclude_dir(self, path: str) -> bool:
        apath = os.path.abspath(path)
        name = os.path.basename(apath).rstrip("/")

        if self.is_blacklisted_dirname(name):
            return True

        parts = [p.rstrip("/") for p in apath.split(os.sep) if p]

        if any(p in self.dirnames for p in parts):
            return True

        for dp in self.dirpaths:
            if apath == dp or apath.startswith(dp + os.sep):
                return True

        return False

    def include_file_by_only_rule(self, path: str) -> bool:
        if not self.only_exts and not self.only_patterns:
            return True

        base = os.path.basename(path)
        ext = get_file_extension(path)
        rel = os.path.relpath(os.path.abspath(path), self.base_dir)

        if ext in self.only_exts:
            return True

        for pattern in self.only_patterns:
            if fnmatch.fnmatch(base, pattern) or fnmatch.fnmatch(rel, pattern):
                return True

        return False

    def exclude_file(self, path: str) -> bool:
        apath = os.path.abspath(path)
        base = os.path.basename(apath).lower()
        ext = get_file_extension(apath)

        parts = [p.rstrip("/") for p in apath.split(os.sep) if p]
        parent_parts = parts[:-1]

        if self.use_default_blacklist and any(p in DEFAULT_BLACKLIST_DIRS for p in parent_parts):
            return True

        for dp in self.dirpaths:
            if apath == dp or apath.startswith(dp + os.sep):
                return True

        if any(p in self.dirnames for p in parent_parts):
            return True

        if base in self.filenames:
            return True

        if ext and ext in self.exclude_exts:
            return True

        if not self.include_file_by_only_rule(apath):
            return True

        return False


def iter_filtered_files(base_dir: str, excl: Exclusions) -> Iterable[str]:
    for root, dirs, files in os.walk(base_dir):
        abs_dir = os.path.abspath(root)

        dirs[:] = [
            d for d in sorted(dirs)
            if not excl.exclude_dir(os.path.join(abs_dir, d))
        ]

        for fname in sorted(files):
            abs_fp = os.path.abspath(os.path.join(root, fname))

            if excl.exclude_file(abs_fp):
                continue

            ext = get_file_extension(abs_fp)
            if ext not in WHITELIST_EXTS:
                continue

            yield abs_fp


def render_tree(base_dir: str, excl: Exclusions, color: bool = True) -> Text:
    console_text = Text()

    def walk(directory: str, prefix: str = "") -> None:
        try:
            items = sorted(os.listdir(directory))
        except PermissionError:
            return

        visible_items: list[str] = []

        for item in items:
            path = os.path.join(directory, item)

            if os.path.isdir(path):
                if excl.exclude_dir(path):
                    continue

                before = len(visible_items)
                has_visible = any(
                    True for _ in iter_preview_files(path, excl, limit=1)
                )

                if has_visible:
                    visible_items.append(item)
                elif before == len(visible_items):
                    continue

            elif os.path.isfile(path):
                ext = get_file_extension(path)
                if ext in WHITELIST_EXTS and not excl.exclude_file(path):
                    visible_items.append(item)

        for idx, item in enumerate(visible_items):
            path = os.path.join(directory, item)
            is_dir = os.path.isdir(path)
            is_last = idx == len(visible_items) - 1

            branch = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")

            icon, style = icon_for(path, is_dir)

            console_text.append(prefix + branch, style=AnsiStyle.DIM.rich)
            if color:
                console_text.append(f"{icon} {item}", style=style.rich)
            else:
                console_text.append(f"{icon} {item}")
            console_text.append("\n")

            if is_dir:
                walk(path, next_prefix)

    walk(base_dir)
    return console_text


def iter_preview_files(base_dir: str, excl: Exclusions, limit: int = 1) -> Iterable[str]:
    count = 0
    for f in iter_filtered_files(base_dir, excl):
        yield f
        count += 1
        if count >= limit:
            return


def format_markdown(base_dir: str, excl: Exclusions) -> str:
    out: list[str] = []

    for abs_fp in iter_filtered_files(base_dir, excl):
        rel_path = os.path.relpath(abs_fp, base_dir)
        ext = get_file_extension(abs_fp)

        if ext in IMAGE_EXTS:
            out.append(f"\n## {rel_path}\n")
            out.append(f"[binary/image file skipped from content dump: {ext}]")
            continue

        out.append(f"\n## {rel_path}\n")
        out.append(f"```{ext}")

        try:
            with open(abs_fp, "r", encoding="utf-8") as f:
                out.append(f.read())
        except UnicodeDecodeError:
            out.append(f"Error reading file {rel_path}: not valid UTF-8 text")
        except Exception as e:
            out.append(f"Error reading file {rel_path}: {e}")

        out.append("```")

    return "\n".join(out)


def format_xml(base_dir: str, excl: Exclusions) -> str:
    root_elem = ET.Element("directory")

    for abs_fp in iter_filtered_files(base_dir, excl):
        rel_path = os.path.relpath(abs_fp, base_dir)
        ext = get_file_extension(abs_fp)

        file_elem = ET.SubElement(root_elem, "file")

        path_elem = ET.SubElement(file_elem, "path")
        path_elem.text = rel_path

        lang_elem = ET.SubElement(file_elem, "language")
        lang_elem.text = ext

        content_elem = ET.SubElement(file_elem, "content")

        if ext in IMAGE_EXTS:
            content_elem.text = f"[binary/image file skipped from content dump: {ext}]"
            continue

        try:
            with open(abs_fp, "r", encoding="utf-8") as f:
                content_elem.text = f.read()
        except UnicodeDecodeError:
            content_elem.text = f"Error reading file {rel_path}: not valid UTF-8 text"
        except Exception as e:
            content_elem.text = f"Error reading file {rel_path}: {e}"

    xml_str = ET.tostring(root_elem, encoding="unicode")
    parsed = minidom.parseString(xml_str)
    return parsed.toprettyxml(indent="  ")


def build_output(
    base_dir: str,
    output_format: str,
    excl: Exclusions,
    show_tree: bool,
    color: bool,
) -> str:
    console = Console(record=True, file=io.StringIO(), force_terminal=color, width=140)
    sections: list[str] = []

    if show_tree:
        console.print("# Directory Structure", style="bold")
        tree_text = render_tree(base_dir, excl, color=color)
        console.print(tree_text if tree_text.plain.strip() else "(no matching files)")
        sections.append(console.export_text(styles=color))

    sections.append(f"# File Contents ({output_format.capitalize()} Format)")

    if output_format == "markdown":
        sections.append(format_markdown(base_dir, excl))
    elif output_format == "xml":
        sections.append(format_xml(base_dir, excl))
    else:
        raise ValueError("Invalid output format.")

    return "\n".join(sections)


def copy_to_clipboard(text: str) -> None:
    candidates = [
        ["xclip", "-selection", "clipboard"],
        ["wl-copy"],
        ["pbcopy"],
    ]

    for cmd in candidates:
        try:
            subprocess.run(cmd, input=text, text=True, check=True)
            print(f"\nContent copied to clipboard using {cmd[0]}!")
            return
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"\nClipboard command {cmd[0]} failed: {e}", file=sys.stderr)

    print(
        "\nUnable to copy to clipboard. Install xclip, wl-clipboard, or use pbcopy on macOS.",
        file=sys.stderr,
    )


def path_is_excluded_by_interactive(path: str, excluded_paths: Set[str]) -> bool:
    apath = os.path.abspath(path)

    for ex in excluded_paths:
        if apath == ex or apath.startswith(ex + os.sep):
            return True

    return False


@dataclass(frozen=True)
class SelectorEntry:
    path: str
    is_dir: bool


class InteractiveSelectorApp(App[Optional[Set[str]]]):
    CSS = """
    Screen {
        layout: vertical;
    }

    #help {
        dock: top;
        padding: 0 1;
        color: $text-muted;
        background: $surface;
    }

    Tree {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("space", "toggle_excluded", "Toggle exclude", show=True, priority=True),
        Binding("enter", "toggle_node", "Open/close", show=True, priority=True),
        Binding("g", "submit", "Generate", show=True, priority=True),
        Binding("q", "quit_without_submit", "Quit", show=True, priority=True),
    ]

    def __init__(self, base_dir: str, base_excl: Exclusions) -> None:
        super().__init__()
        self.base_dir = os.path.abspath(base_dir)
        self.base_excl = base_excl
        self.excluded_paths: Set[str] = set()
        self.path_nodes: dict[str, object] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(
            "Space toggles exclusions. Enter opens folders. Press g to generate, q to quit.",
            id="help",
        )
        tree: TextualTree[SelectorEntry] = TextualTree(
            self._label_for(self.base_dir, is_dir=True),
            data=SelectorEntry(self.base_dir, True),
        )
        tree.root.expand()
        yield tree
        yield Footer()

    def on_mount(self) -> None:
        self.title = "catallx"
        self.sub_title = self.base_dir
        tree = self.query_one(TextualTree)
        self.path_nodes[self.base_dir] = tree.root
        self._populate_tree(tree)
        tree.focus()

    def _label_for(self, path: str, is_dir: bool) -> Text:
        icon, style = icon_for(path, is_dir)
        name = os.path.basename(path.rstrip(os.sep)) or path
        if is_dir:
            name = f"{name}/"

        excluded = path_is_excluded_by_interactive(path, self.excluded_paths)
        marker = "[x]" if excluded else "[ ]"
        text = Text(f"{marker} {icon} {name}", style=AnsiStyle.RED.rich if excluded else style.rich)

        if excluded:
            text.stylize("bold")

        return text

    def _populate_tree(self, tree: TextualTree[SelectorEntry]) -> None:
        def add_children(parent_node: object, directory: str) -> None:
            try:
                items = sorted(os.listdir(directory))
            except PermissionError:
                return

            for item in items:
                path = os.path.abspath(os.path.join(directory, item))
                is_dir = os.path.isdir(path)

                if is_dir:
                    if self.base_excl.exclude_dir(path):
                        continue
                    if not any(True for _ in iter_preview_files(path, self.base_excl, limit=1)):
                        continue

                    child = parent_node.add(
                        self._label_for(path, is_dir=True),
                        data=SelectorEntry(path, True),
                    )
                    self.path_nodes[path] = child
                    add_children(child, path)
                    continue

                if not os.path.isfile(path):
                    continue

                ext = get_file_extension(path)
                if ext not in WHITELIST_EXTS or self.base_excl.exclude_file(path):
                    continue

                child = parent_node.add_leaf(
                    self._label_for(path, is_dir=False),
                    data=SelectorEntry(path, False),
                )
                self.path_nodes[path] = child

        add_children(tree.root, self.base_dir)

    def _refresh_labels(self) -> None:
        for path, node in self.path_nodes.items():
            data = getattr(node, "data", None)
            if isinstance(data, SelectorEntry):
                node.set_label(self._label_for(path, data.is_dir))

    def action_toggle_node(self) -> None:
        tree = self.query_one(TextualTree)
        node = tree.cursor_node
        data = node.data

        if isinstance(data, SelectorEntry) and data.is_dir:
            node.toggle()

    def action_toggle_excluded(self) -> None:
        tree = self.query_one(TextualTree)
        node = tree.cursor_node
        data = node.data

        if not isinstance(data, SelectorEntry):
            return

        path = data.path
        if path_is_excluded_by_interactive(path, self.excluded_paths):
            for excluded in sorted(self.excluded_paths, key=len, reverse=True):
                if path == excluded or path.startswith(excluded + os.sep):
                    self.excluded_paths.remove(excluded)
                    break
        else:
            self.excluded_paths = {
                excluded for excluded in self.excluded_paths
                if not excluded.startswith(path + os.sep)
            }
            self.excluded_paths.add(path)

        self._refresh_labels()

    def action_submit(self) -> None:
        self.exit(self.excluded_paths)

    def action_quit_without_submit(self) -> None:
        self.exit(None)


def interactive_select(base_dir: str, base_excl: Exclusions) -> Optional[Set[str]]:
    return InteractiveSelectorApp(base_dir, base_excl).run()


def add_interactive_exclusions(excl: Exclusions, selected: Set[str]) -> None:
    for path in selected:
        apath = os.path.abspath(path)

        if os.path.isdir(apath):
            excl.dirpaths.add(apath)
        elif os.path.isfile(apath):
            excl.filenames.add(os.path.basename(apath).lower())


def resolve_directory_arg(raw_directory: str, parser: argparse.ArgumentParser) -> str:
    directory = Path(raw_directory).expanduser()

    try:
        resolved = directory.resolve(strict=True)
    except FileNotFoundError:
        parser.error(f"directory does not exist: {raw_directory}")
    except OSError as exc:
        parser.error(f"cannot access directory {raw_directory!r}: {exc}")

    if not resolved.is_dir():
        parser.error(f"path is not a directory: {resolved}")

    return str(resolved)


def main() -> None:
    p = argparse.ArgumentParser(description="Emit filtered colored directory contents in Markdown or XML.")

    p.add_argument("directory", nargs="?", help="Path to the directory")
    p.add_argument("--tree", action="store_true", help="Print filtered directory tree before file contents")
    p.add_argument("--cl", action="store_true", help="Copy full output to clipboard")
    p.add_argument("--format", choices=["markdown", "xml"], default="markdown", help="Output format")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI color in tree output")
    p.add_argument("-i", "--interactive", action="store_true", help="Interactively select inclusions/exclusions")

    p.add_argument(
        "-x",
        "--exclude",
        help="Comma-separated excludes: extensions like py/.py, filenames, or subtrees like build/*.",
    )

    p.add_argument(
        "-d",
        "--exclude-dirs",
        help="Comma-separated directory names to exclude anywhere, e.g. env,venv,acquisition.",
    )

    p.add_argument(
        "-a",
        "--only",
        help="Comma-separated include rules. Examples: py, .py, '*.py', Dockerfile.",
    )

    p.add_argument(
        "--no-default-blacklist",
        action="store_true",
        help="Disable default blacklist directories like .git, node_modules, __pycache__, .venv.",
    )

    if len(sys.argv) == 1:
        p.print_help()
        return

    args = p.parse_args()

    if not args.directory:
        p.error("directory is required")

    base_dir = resolve_directory_arg(args.directory, p)

    excl = Exclusions(
        base_dir=base_dir,
        use_default_blacklist=not args.no_default_blacklist,
    )

    excl.add_dirnames(args.exclude_dirs)
    excl.add_generic_csv(args.exclude)
    excl.add_only_csv(args.only)

    if args.interactive:
        selected = interactive_select(base_dir, excl)
        if selected is None:
            print("Quit.")
            return
        add_interactive_exclusions(excl, selected)

    output = build_output(
        base_dir=base_dir,
        output_format=args.format,
        excl=excl,
        show_tree=args.tree or args.interactive,
        color=not args.no_color,
    )

    print(output)

    if args.cl:
        copy_to_clipboard(output)


if __name__ == "__main__":
    main()
