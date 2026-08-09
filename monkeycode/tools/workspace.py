from __future__ import annotations

from pathlib import Path


class WorkspaceError(ValueError):
    pass


class WorkspaceGuard:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root.resolve()

    def resolve(self, path: str | Path) -> Path:
        raw_path = Path(path)
        candidate = raw_path if raw_path.is_absolute() else self.workspace_root / raw_path
        resolved = candidate.resolve()
        if resolved != self.workspace_root and self.workspace_root not in resolved.parents:
            raise WorkspaceError(f"path is outside workspace: {path}")
        return resolved

    def relative(self, path: str | Path) -> str:
        return self.resolve(path).relative_to(self.workspace_root).as_posix()
