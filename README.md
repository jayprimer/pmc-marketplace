# PMC Plugins Marketplace

A Claude Code plugin marketplace for [PMC (Project Manager Claude)](https://github.com/jayprimer/pm-claude) skills.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add jayprimer/pmc-marketplace
```

Then install the PMC plugin:

```
/plugin install pmc@pmc-plugins
```

## Available Plugins

### pmc

Project management and knowledge base skills for Claude Code.

**Skills included:**

| Skill | Description |
|-------|-------------|
| `kb` | Knowledge base management - read and understand project documentation |
| `memory` | Quick context capture and retrieval |
| `plan` | Create structured implementation plans |
| `dev` | Development workflow assistance |
| `ticket-status` | Track ticket/task status |
| `validate` | Validate project artifacts |
| `workflow` | Workflow definition and execution |
| `complete` | Task completion workflow |
| `inbox` | Manage incoming tasks and requests |
| `reflect` | Session reflection and learning |
| `test` | Test planning and execution |
| `lint-kb` | Lint knowledge base documents |
| `lint-skill` | Lint skill definitions |
| `plan-validation` | Validate implementation plans |
| `update-kb` | Update knowledge base documents |

## Usage

After installation, use skills with the `/pmc:` prefix:

```
/pmc:kb          # Access knowledge base
/pmc:memory      # Manage memory/context
/pmc:plan        # Create implementation plans
/pmc:dev         # Development assistance
```

## License

MIT
