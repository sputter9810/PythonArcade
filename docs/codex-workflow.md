# Codex Workflow

## Objective

Use Codex to accelerate development without sacrificing architecture or UI consistency.

## Rules for Codex tasks

Always provide:
- a clear task goal
- allowed files/folders to modify
- architecture constraints
- UI constraints
- definition of done

## Example instructions

```text
You are working in a Python arcade project using Pygame.

Hard constraints:
- keep game logic separate from rendering
- reuse shared theme and UI modules
- avoid overlapping text/elements
- preserve the registry-driven launcher
- use type hints and docstrings
- avoid giant monolithic files

Task:
[insert exact task]

Files allowed to modify:
[list files]

Definition of done:
[list done criteria]
```

## Best use cases

- implement one game at a time
- build one shared subsystem at a time
- write tests for logic files
- refactor specific scenes
- improve launcher interactions

## Avoid

- asking Codex to create all 16 games in one go
- mixing architecture redesign with game implementation in one task
- allowing unrestricted edits across the entire repo
