# Source: https://docs.claude.com/en/docs/agent-sdk/overview

---

# Agent SDK overview

Build production AI agents with Claude Code as a library

The Claude Code SDK has been renamed to the Claude Agent SDK. If you're migrating from the old SDK, see the [Migration Guide](/docs/en/agent-sdk/migration-guide).

Build AI agents that autonomously read files, run commands, search the web, edit code, and more. The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.

Python

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"])
    ):
        print(message)  # Claude reads the file, finds the bug, edits it

asyncio.run(main())
```

The Agent SDK includes built-in tools for reading files, running commands, and editing code, so your agent can start working immediately without you implementing tool execution. Dive into the quickstart or explore real agents built with the SDK:

[Quickstart

Build a bug-fixing agent in minutes](/docs/en/agent-sdk/quickstart)[Example agents

Email assistant, research agent, and more](https://github.com/anthropics/claude-agent-sdk-demos)

## Capabilities

Everything that makes Claude Code powerful is available in the SDK:

Built-in tools

Built-in tools

Hooks

Hooks

Subagents

Subagents

MCP

MCP

Permissions

Permissions

Sessions

Sessions

### Claude Code features

The SDK also supports Claude Code's filesystem-based configuration. To use these features, set `setting_sources=["project"]` (Python) or `settingSources: ['project']` (TypeScript) in your options.

| Feature | Description | Location |
| --- | --- | --- |
| [Skills](/docs/en/agent-sdk/skills) | Specialized capabilities defined in Markdown | `.claude/skills/SKILL.md` |
| [Slash commands](/docs/en/agent-sdk/slash-commands) | Custom commands for common tasks | `.claude/commands/*.md` |
| [Memory](/docs/en/agent-sdk/modifying-system-prompts) | Project context and instructions | `CLAUDE.md` or `.claude/CLAUDE.md` |
| [Plugins](/docs/en/agent-sdk/plugins) | Extend with custom commands, agents, and MCP servers | Programmatic via `plugins` option |

## Get started

1. 1

   Install Claude Code

   The SDK uses Claude Code as its runtime:

   macOS/Linux/WSL

   macOS/Linux/WSL

   Homebrew

   Homebrew

   npm

   npm

   See [Claude Code setup](https://docs.anthropic.com/en/docs/claude-code/setup) for Windows and other options.
2. 2

   Install the SDK

   TypeScript

   TypeScript

   Python

   Python
3. 3

   Set your API key

   ```
   export ANTHROPIC_API_KEY=your-api-key
   ```

   Get your key from the [Console](https://console.anthropic.com/).

   The SDK also supports authentication via third-party API providers:

   * **Amazon Bedrock**: Set `CLAUDE_CODE_USE_BEDROCK=1` environment variable and configure AWS credentials
   * **Google Vertex AI**: Set `CLAUDE_CODE_USE_VERTEX=1` environment variable and configure Google Cloud credentials
   * **Microsoft Foundry**: Set `CLAUDE_CODE_USE_FOUNDRY=1` environment variable and configure Azure credentials

   Unless previously approved, we do not allow third party developers to offer Claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK. Please use the API key authentication methods described in this document instead.
4. 4

   Run your first agent

   This example creates an agent that lists files in your current directory using built-in tools.

   Python

   ```
   import asyncio
   from claude_agent_sdk import query, ClaudeAgentOptions

   async def main():
       async for message in query(
           prompt="What files are in this directory?",
           options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"])
       ):
           print(message)

   asyncio.run(main())
   ```

**Ready to build?** Follow the [Quickstart](/docs/en/agent-sdk/quickstart) to create an agent that finds and fixes bugs in minutes.

## Compare the Agent SDK to other Claude tools

The Claude platform offers multiple ways to build with Claude. Here's how the Agent SDK fits in:

Agent SDK vs Client SDK

Agent SDK vs Client SDK

Agent SDK vs Claude Code CLI

Agent SDK vs Claude Code CLI

## Changelog

View the full changelog for SDK updates, bug fixes, and new features:

* **TypeScript SDK**: [View CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)
* **Python SDK**: [View CHANGELOG.md](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)

## Reporting bugs

If you encounter bugs or issues with the Agent SDK:

* **TypeScript SDK**: [Report issues on GitHub](https://github.com/anthropics/claude-agent-sdk-typescript/issues)
* **Python SDK**: [Report issues on GitHub](https://github.com/anthropics/claude-agent-sdk-python/issues)

## Branding guidelines

For partners integrating the Claude Agent SDK, use of Claude branding is optional. When referencing Claude in your product:

**Allowed:**

* "Claude Agent" (preferred for dropdown menus)
* "Claude" (when within a menu already labeled "Agents")
* "{YourAgentName} Powered by Claude" (if you have an existing agent name)

**Not permitted:**

* "Claude Code" or "Claude Code Agent"
* Claude Code-branded ASCII art or visual elements that mimic Claude Code

Your product should maintain its own branding and not appear to be Claude Code or any Anthropic product. For questions about branding compliance, contact our [sales team](https://www.anthropic.com/contact-sales).

## License and terms

Use of the Claude Agent SDK is governed by [Anthropic's Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms), including when you use it to power products and services that you make available to your own customers and end users, except to the extent a specific component or dependency is covered by a different license as indicated in that component's LICENSE file.

## Next steps

[Quickstart

Build an agent that finds and fixes bugs in minutes](/docs/en/agent-sdk/quickstart)[Example agents

Email assistant, research agent, and more](https://github.com/anthropics/claude-agent-sdk-demos)[TypeScript SDK

Full TypeScript API reference and examples](/docs/en/agent-sdk/typescript)[Python SDK

Full Python API reference and examples](/docs/en/agent-sdk/python)

* [Capabilities](#capabilities)
* [Claude Code features](#claude-code-features)
* [Get started](#get-started)
* [Compare the Agent SDK to other Claude tools](#compare-the-agent-sdk-to-other-claude-tools)
* [Changelog](#changelog)
* [Reporting bugs](#reporting-bugs)
* [Branding guidelines](#branding-guidelines)
* [License and terms](#license-and-terms)
* [Next steps](#next-steps)
