# Source: https://code.claude.com/docs/en/overview

---

# Claude Code overview

Learn about Claude Code, Anthropic’s agentic coding tool that lives in your terminal and helps you turn ideas into code faster than ever before.

## [​](#get-started-in-30-seconds) Get started in 30 seconds

Prerequisites:

* A [Claude.ai](https://claude.ai) (recommended) or [Claude Console](https://console.anthropic.com/) account

**Install Claude Code:**
To install Claude Code, use one of the following methods:

* Native Install (Recommended)
* Homebrew
* NPM

**macOS, Linux, WSL:**

```
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**

```
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**

```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

```
brew install --cask claude-code
```

If you have [Node.js 18 or newer installed](https://nodejs.org/en/download/):

```
npm install -g @anthropic-ai/claude-code
```

**Start using Claude Code:**

```
cd your-project
claude
```

You’ll be prompted to log in on first use. That’s it! [Continue with Quickstart (5 minutes) →](/docs/en/quickstart)

Claude Code automatically keeps itself up to date. See [advanced setup](/docs/en/setup) for installation options, manual updates, or uninstallation instructions. Visit [troubleshooting](/docs/en/troubleshooting) if you hit issues.

## [​](#what-claude-code-does-for-you) What Claude Code does for you

* **Build features from descriptions**: Tell Claude what you want to build in plain English. It will make a plan, write the code, and ensure it works.
* **Debug and fix issues**: Describe a bug or paste an error message. Claude Code will analyze your codebase, identify the problem, and implement a fix.
* **Navigate any codebase**: Ask anything about your team’s codebase, and get a thoughtful answer back. Claude Code maintains awareness of your entire project structure, can find up-to-date information from the web, and with [MCP](/docs/en/mcp) can pull from external data sources like Google Drive, Figma, and Slack.
* **Automate tedious tasks**: Fix fiddly lint issues, resolve merge conflicts, and write release notes. Do all this in a single command from your developer machines, or automatically in CI.

## [​](#why-developers-love-claude-code) Why developers love Claude Code

* **Works in your terminal**: Not another chat window. Not another IDE. Claude Code meets you where you already work, with the tools you already love.
* **Takes action**: Claude Code can directly edit files, run commands, and create commits. Need more? [MCP](/docs/en/mcp) lets Claude read your design docs in Google Drive, update your tickets in Jira, or use *your* custom developer tooling.
* **Unix philosophy**: Claude Code is composable and scriptable. `tail -f app.log | claude -p "Slack me if you see any anomalies appear in this log stream"` *works*. Your CI can run `claude -p "If there are new text strings, translate them into French and raise a PR for @lang-fr-team to review"`.
* **Enterprise-ready**: Use the Claude API, or host on AWS or GCP. Enterprise-grade [security](/docs/en/security), [privacy](/docs/en/data-usage), and [compliance](https://trust.anthropic.com/) is built-in.

## [​](#next-steps) Next steps

[## Quickstart

See Claude Code in action with practical examples](/docs/en/quickstart)[## Common workflows

Step-by-step guides for common workflows](/docs/en/common-workflows)[## Troubleshooting

Solutions for common issues with Claude Code](/docs/en/troubleshooting)[## IDE setup

Add Claude Code to your IDE](/docs/en/vs-code)

## [​](#additional-resources) Additional resources

[## Build with the Agent SDK

Create custom AI agents with the Claude Agent SDK](https://docs.claude.com/en/docs/agent-sdk/overview)[## Host on AWS or GCP

Configure Claude Code with Amazon Bedrock or Google Vertex AI](/docs/en/third-party-integrations)[## Settings

Customize Claude Code for your workflow](/docs/en/settings)[## Commands

Learn about CLI commands and controls](/docs/en/cli-reference)[## Reference implementation

Clone our development container reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer)[## Security

Discover Claude Code’s safeguards and best practices for safe usage](/docs/en/security)[## Privacy and data usage

Understand how Claude Code handles your data](/docs/en/data-usage)

Was this page helpful?

YesNo

[Quickstart](/docs/en/quickstart)

⌘I

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Company

[Anthropic](https://www.anthropic.com/company)[Careers](https://www.anthropic.com/careers)[Economic Futures](https://www.anthropic.com/economic-futures)[Research](https://www.anthropic.com/research)[News](https://www.anthropic.com/news)[Trust center](https://trust.anthropic.com/)[Transparency](https://www.anthropic.com/transparency)

Help and security

[Availability](https://www.anthropic.com/supported-countries)[Status](https://status.anthropic.com/)[Support center](https://support.claude.com/)

Learn

[Courses](https://www.anthropic.com/learn)[MCP connectors](https://claude.com/partners/mcp)[Customer stories](https://www.claude.com/customers)[Engineering blog](https://www.anthropic.com/engineering)[Events](https://www.anthropic.com/events)[Powered by Claude](https://claude.com/partners/powered-by-claude)[Service partners](https://claude.com/partners/services)[Startups program](https://claude.com/programs/startups)
