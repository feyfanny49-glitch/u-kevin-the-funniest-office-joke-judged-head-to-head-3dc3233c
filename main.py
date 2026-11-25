#!/usr/bin/env python3
"""Entry for make.fun "The Funniest Office Joke, Judged Head to Head".

Writes the one judged text to /output/entry.txt and nothing else in /output.

The gate (house scorer) wants UTF-8 text of 1 to 200 characters, not only white
space, and refuses a mode-0600 artifact, so:

  * the text is a literal in this file (no network, no env, no outside file);
  * the bytes are gate-checked here, before anything is written;
  * the artifact is written to a temp file in the same directory, chmodded to
    0644 *before* os.replace moves it into place (tempfile.mkstemp is never
    used: it creates 0600, which the gate refuses);
  * after the replace the mode, the bytes on disk and the character count are
    read back and checked again, and a mismatch is a hard failure;
  * the temp file is removed on any failure, so /output holds only entry.txt.

Stdlib only, deterministic: two runs write byte-identical files.
"""

from __future__ import annotations

import hashlib
import os
import sys

OUT_DIR = "/output"
OUT_NAME = "entry.txt"
MODE = 0o644
MIN_CHARS = 1
MAX_CHARS = 200

# The whole entry: one line of office life, setup then turn, punchline last.
ENTRY = (
    "No budget for my raise, but plenty for team-building paintball. "
    "I shot my manager in the back, and honestly, it built the team."
)


class EntryError(RuntimeError):
    """The entry or the artifact failed a check."""


def gate_check(text: str) -> bytes:
    """Check the entry the way the gate scorer does and return its bytes."""
    try:
        data = text.encode("utf-8")
        text.encode("utf-8").decode("utf-8")
    except UnicodeError as exc:  # pragma: no cover - the literal is valid UTF-8
        raise EntryError(f"entry is not valid UTF-8: {exc}") from exc

    chars = len(text)
    if not (MIN_CHARS <= chars <= MAX_CHARS):
        raise EntryError(f"entry is {chars} characters, outside {MIN_CHARS}..{MAX_CHARS}")
    if not text.strip():
        raise EntryError("entry is only white space")
    if data[:1].isspace() or data[-1:].isspace():
        raise EntryError("entry starts or ends with white space")
    if data.endswith(b"\n"):
        raise EntryError("entry carries a trailing newline; the exact bytes are the entry")
    return data


def write_atomically(data: bytes, out_dir: str, name: str) -> str:
    """Write data to out_dir/name atomically, at mode 0644, and return the path."""
    os.makedirs(out_dir, exist_ok=True)
    final_path = os.path.join(out_dir, name)
    tmp_path = os.path.join(out_dir, "." + name + ".tmp")

    # Clear a temp left behind by an interrupted earlier run.
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

    try:
        fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, MODE)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_path, MODE)  # umask-proof: done before the replace
        os.replace(tmp_path, final_path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
    return final_path


def verify(path: str, data: bytes) -> dict[str, object]:
    """Read the artifact back and hold it to the gate, strictly."""
    st = os.stat(path)
    mode = st.st_mode & 0o777
    with open(path, "rb") as fh:
        on_disk = fh.read()

    if mode != MODE:
        raise EntryError(f"{path} is mode {oct(mode)}, not {oct(MODE)}")
    if on_disk != data:
        raise EntryError(f"{path} does not hold the entry bytes")
    try:
        text = on_disk.decode("utf-8")
    except UnicodeError as exc:  # pragma: no cover
        raise EntryError(f"{path} is not valid UTF-8: {exc}") from exc

    chars = len(text)
    if not (MIN_CHARS <= chars <= MAX_CHARS) or not text.strip():
        raise EntryError(f"{path} fails the gate: {chars} characters")

    leftovers = sorted(n for n in os.listdir(os.path.dirname(path)) if n != os.path.basename(path))
    if leftovers:
        raise EntryError(f"/output holds more than the artifact: {leftovers}")

    return {
        "path": path,
        "bytes": len(on_disk),
        "chars": chars,
        "mode": oct(mode),
        "sha256": hashlib.sha256(on_disk).hexdigest(),
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out_dir = OUT_DIR
    if argv:
        if len(argv) == 2 and argv[0] == "--out-dir":  # local test hook only
            out_dir = argv[1]
        else:
            print(f"usage: {os.path.basename(__file__)} [--out-dir <dir>]", file=sys.stderr)
            return 2

    try:
        data = gate_check(ENTRY)
        path = write_atomically(data, out_dir, OUT_NAME)
        info = verify(path, data)
    except EntryError as exc:
        print(f"entry refused: {exc}", file=sys.stderr)
        return 1

    print(ENTRY)
    print(
        "wrote {path}: {bytes} bytes, {chars} chars, mode {mode}, sha256 {sha256}".format(**info)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
