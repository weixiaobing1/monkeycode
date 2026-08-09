from __future__ import annotations

from pathlib import Path

from monkeycode.messages import ToolCall
from monkeycode.permissions import PermissionMode
from monkeycode.tools.executor import ToolExecutor
from monkeycode.tools.files import EditFileTool, ReadFileTool, WriteFileTool
from monkeycode.tools.registry import ToolRegistry


def executor(tmp_path: Path) -> ToolExecutor:
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    return ToolExecutor(registry, workspace_root=tmp_path, permission_mode=PermissionMode.ALLOW)


def call(name: str, arguments_json: str) -> ToolCall:
    return ToolCall(id="call_1", name=name, arguments_json=arguments_json)


def test_read_and_write_file_inside_workspace(tmp_path: Path) -> None:
    tool_executor = executor(tmp_path)

    write = tool_executor.execute(call("write_file", '{"path":"notes/a.txt","content":"hello"}'))
    read = tool_executor.execute(call("read_file", '{"path":"notes/a.txt"}'))

    assert write.success is True
    assert read.success is True
    assert read.output["content"] == "hello"


def test_file_tools_reject_workspace_escape(tmp_path: Path) -> None:
    result = executor(tmp_path).execute(call("read_file", '{"path":"../secret.txt"}'))

    assert result.success is False
    assert result.error_type == "path_outside_workspace"


def test_read_file_rejects_directory(tmp_path: Path) -> None:
    result = executor(tmp_path).execute(call("read_file", '{"path":"."}'))

    assert result.success is False
    assert result.error_type == "is_directory"


def test_read_file_description_explains_selection_boundary() -> None:
    assert "exact path is already known" in ReadFileTool.description
    assert "Do not use it merely to discover files" in ReadFileTool.description


def test_edit_file_replaces_only_unique_match(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("one two three", encoding="utf-8")

    result = executor(tmp_path).execute(
        call("edit_file", '{"path":"a.txt","old_text":"two","new_text":"TWO"}')
    )

    assert result.success is True
    assert target.read_text(encoding="utf-8") == "one TWO three"


def test_edit_file_does_not_modify_on_zero_or_multiple_matches(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("one one", encoding="utf-8")
    tool_executor = executor(tmp_path)

    missing = tool_executor.execute(
        call("edit_file", '{"path":"a.txt","old_text":"two","new_text":"TWO"}')
    )
    multiple = tool_executor.execute(
        call("edit_file", '{"path":"a.txt","old_text":"one","new_text":"ONE"}')
    )

    assert missing.error_type == "old_text_not_found"
    assert multiple.error_type == "old_text_not_unique"
    assert target.read_text(encoding="utf-8") == "one one"
