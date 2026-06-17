"""Track generated files — write-on-change plus drift detection.

A small, project-agnostic take on the "managed generated files" paradigm: a generator
records each output's content hash in a JSON manifest, so it can write only what changed
and a separate check can tell whether the committed/working outputs still match what the
generator would produce — catching a hand-edit of generated output, or a stale output
whose source moved on. Stdlib only; no framework coupling.

    m = Manifest.load("tasks/.gen-manifest.json", salt=TOOL_VERSION)
    for target, content in render_all():
        m.write(target, content, sources=[...])   # writes only if changed
    dropped = m.prune(keep=[t for t, _ in render_all()])  # forget vanished targets
    m.save()
    drifted = m.stale()                            # hand-edited / missing outputs (== drift)
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .fs import write_if_changed


def content_hash(content: str, *, salt: str = "") -> str:
    """sha256 of *content*. An optional *salt* (e.g. a tool version) is folded in, so
    bumping it forces every output to count as changed."""
    h = hashlib.sha256()
    if salt:
        h.update(salt.encode("utf-8"))
        h.update(b"\0")
    h.update(content.encode("utf-8"))
    return "sha256:" + h.hexdigest()


@dataclass
class Manifest:
    """A `target -> {hash, sources}` record persisted as JSON.

    `salt` folds into every hash (pass a tool/version string to force regen on a bump).
    Targets are stored as strings; `write`/`stale`/`prune` operate relative to wherever
    the process runs (normally the repo root, like the rest of `tasks/`).
    """

    path: Path
    salt: str = ""
    files: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path, *, salt: str = "") -> Manifest:
        p = Path(path)
        files: dict = {}
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data.get("files"), dict):
                    files = data["files"]
            except (json.JSONDecodeError, OSError):
                files = {}
        return cls(p, salt, files)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        body = {"salt": self.salt, "files": self.files}
        self.path.write_text(
            json.dumps(body, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def write(
        self, target: str | Path, content: str, *, sources: Iterable[str | Path] = ()
    ) -> bool:
        """Write *content* to *target* only if it changed; **always** record its hash.

        The hash and sources are recorded unconditionally — even when the file was
        unchanged — because the manifest reflects what the generator *intends*, so
        `stale()` can later spot a hand-edit. Returns True iff the file was written; a
        hand-edited output differs from *content*, so it is overwritten (the generator
        wins).
        """
        target = str(target)
        wrote = write_if_changed(target, content)
        self.files[target] = {
            "hash": content_hash(content, salt=self.salt),
            "sources": list(sources),
        }
        return wrote

    def stale(self) -> list[str]:
        """Tracked targets whose on-disk content no longer matches the recorded hash —
        hand-edited, missing, or unreadable. Empty means everything matches the manifest."""
        out = []
        for target, entry in sorted(self.files.items()):
            p = Path(target)
            try:
                matches = p.is_file() and content_hash(
                    p.read_text(encoding="utf-8"), salt=self.salt
                ) == entry.get("hash")
            except (UnicodeDecodeError, OSError):
                matches = False  # unreadable / non-UTF-8 counts as drift
            if not matches:
                out.append(target)
        return out

    def prune(self, keep: Iterable[str | Path]) -> list[str]:
        """Drop manifest entries whose target is not in *keep* (an iterable of targets).

        Returns the dropped targets so the caller can delete their files if it owns them
        (this only forgets them — it never touches the filesystem)."""
        keep = {str(k) for k in keep}
        dropped = [t for t in self.files if t not in keep]
        for t in dropped:
            del self.files[t]
        return dropped
