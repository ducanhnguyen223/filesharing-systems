<!-- KNOWNS GUIDELINES START -->
# Knowns Guidelines

## Session Init (Required)
```json
mcp__knowns__detect_projects({})
mcp__knowns__set_project({ "projectRoot": "/path/to/project" })
```

## Critical Rules
- Never edit .md files directly — use MCP tools
- Read docs BEFORE planning or coding
- Plan → Approve → Code (wait for approval)
- Check AC only AFTER completing work
- `start_time` when taking task, `stop_time` when done
- Run `validate` before marking task done
- Use `appendNotes` (not `notes`) to avoid overwriting history

## CLI Pitfalls
- `task create/edit -a` = `--assignee` (NOT acceptance criteria!)
- Use `--ac "text"` to add acceptance criteria
- `--plain` only works with view/list/search, not create/edit
- Subtasks: `--parent 48` (raw ID, not `task-48`)

## References: `@task-<id>` | `@doc/<path>` | `@template/<name>`
<!-- KNOWNS GUIDELINES END -->
