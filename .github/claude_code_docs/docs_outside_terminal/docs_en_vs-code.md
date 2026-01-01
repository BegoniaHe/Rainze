# Source: https://code.claude.com/docs/en/vs-code

---

# Use Claude Code in VS Code

Install and configure the Claude Code extension for VS Code. Get AI coding assistance with inline diffs, @-mentions, plan review, and keyboard shortcuts.

![VS Code editor with the Claude Code extension panel open on the right side, showing a conversation with Claude](https://mintcdn.com/claude-code/-YhHHmtSxwr7W8gy/images/vs-code-extension-interface.jpg?fit=max&auto=format&n=-YhHHmtSxwr7W8gy&q=85&s=300652d5678c63905e6b0ea9e50835f8)
The VS Code extension provides a native graphical interface for Claude Code, integrated directly into your IDE. This is the recommended way to use Claude Code in VS Code.
With the extension, you can review and edit Claude’s plans before accepting them, auto-accept edits as they’re made, @-mention files with specific line ranges from your selection, access conversation history, and open multiple conversations in separate tabs or windows.

## [​](#prerequisites) Prerequisites

* VS Code 1.98.0 or higher
* An Anthropic account (you’ll sign in when you first open the extension). If you’re using a third-party provider like Amazon Bedrock or Google Vertex AI, see [Use third-party providers](#use-third-party-providers) instead.

You don’t need to install the Claude Code CLI first. However, some features like MCP server configuration require the CLI. See [VS Code extension vs. Claude Code CLI](#vs-code-extension-vs-claude-code-cli) for details.

## [​](#install-the-extension) Install the extension

Click the link for your IDE to install directly:

* Install for VS Code
* Install for Cursor

Or in VS Code, press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux) to open the Extensions view, search for “Claude Code”, and click **Install**.

You may need to restart VS Code or run “Developer: Reload Window” from the Command Palette after installation.

## [​](#get-started) Get started

Once installed, you can start using Claude Code through the VS Code interface:

1

Open the Claude Code panel

Throughout VS Code, the Spark icon indicates Claude Code: ![Spark icon](https://mintcdn.com/claude-code/mfM-EyoZGnQv8JTc/images/vs-code-spark-icon.svg?fit=max&auto=format&n=mfM-EyoZGnQv8JTc&q=85&s=a734d84e785140016672f08e0abb236c)The quickest way to open Claude is to click this icon in the **Editor Toolbar** (top-right corner of the editor). Note: This icon only appears when you have a file open—opening just a folder isn’t enough.![VS Code editor showing the Spark icon in the Editor Toolbar](https://mintcdn.com/claude-code/mfM-EyoZGnQv8JTc/images/vs-code-editor-icon.png?fit=max&auto=format&n=mfM-EyoZGnQv8JTc&q=85&s=eb4540325d94664c51776dbbfec4cf02)Other ways to open Claude Code:

* **Command Palette**: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux), type “Claude Code”, and select an option like “Open in New Tab”
* **Activity Bar**: Run “Claude Code: Open in Side Bar” from the Command Palette once, and a Spark icon will appear in the left sidebar. This is useful if you want quick access without having a file open.

You can drag the Claude panel to reposition it anywhere in VS Code, including to the Activity Bar if the Spark icon isn’t showing there. See [Customize your workflow](#customize-your-workflow) for details.

2

Send a prompt

Prompt Claude Code in the same way you would in the terminal.

3

Review changes

Watch as Claude analyzes your code and suggests changes. Review and accept edits directly in the interface.

## [​](#customize-your-workflow) Customize your workflow

Once you’re up and running, you can reposition the Claude panel or switch to terminal mode.

### [​](#change-the-layout) Change the layout

You can drag the Claude panel to reposition it anywhere in VS Code. Grab the panel’s tab or title bar and drag it to:

* **Activity Bar**: The left sidebar with icons for Explorer, Search, etc.
* **Secondary sidebar**: The right side of the window
* **Editor area**: Opens Claude as a tab alongside your files

This lets you position Claude wherever works best for your workflow.

### [​](#switch-to-terminal-mode) Switch to terminal mode

By default, the extension opens a graphical chat panel. If you prefer the CLI-style interface, open the Use Terminal setting and check the box.
You can also open VS Code settings (`Cmd+,` on Mac or `Ctrl+,` on Windows/Linux), go to Extensions → Claude Code, and check **Use Terminal**.

In terminal mode, the Activity Bar icon (left vertical menu) won’t persist between sessions. If you want the Spark icon to always appear in the Activity Bar, keep this setting disabled and use the Editor Toolbar icon (top-right of editor) to access terminal mode instead.

## [​](#vs-code-commands-and-shortcuts) VS Code commands and shortcuts

Open the Command Palette (`Cmd+Shift+P` on Mac or `Ctrl+Shift+P` on Windows/Linux) and type “Claude Code” to see all available VS Code commands for the Claude Code extension:

These are VS Code commands for controlling the extension. For Claude Code slash commands (like `/help` or `/compact`), not all CLI commands are available in the extension yet. See [VS Code extension vs. Claude Code CLI](#vs-code-extension-vs-claude-code-cli) for details.

| Command | Shortcut | Description |
| --- | --- | --- |
| Focus Input | `Cmd+Esc` (Mac) / `Ctrl+Esc` (Windows/Linux) | Toggle focus between editor and Claude |
| Open in Side Bar | — | Open Claude in the left sidebar |
| Open in Terminal | — | Open Claude in terminal mode |
| Open in New Tab | `Cmd+Shift+Esc` (Mac) / `Ctrl+Shift+Esc` (Windows/Linux) | Open a new conversation as an editor tab |
| Open in New Window | — | Open a new conversation in a separate window |
| New Conversation | `Cmd+N` (Mac) / `Ctrl+N` (Windows/Linux) | Start a new conversation (when Claude is focused) |
| Insert @-Mention Reference | `Alt+K` | Insert a reference to the current file (includes line numbers if text is selected) |
| Show Logs | — | View extension debug logs |
| Logout | — | Sign out of your Anthropic account |

Use **Open in New Tab** or **Open in New Window** to run multiple conversations simultaneously. Each tab or window maintains its own conversation history and context.

## [​](#configure-settings) Configure settings

The extension has two types of settings:

* **Extension settings**: Open with `Cmd+,` (Mac) or `Ctrl+,` (Windows/Linux), then go to Extensions → Claude Code.

  | Setting | Description |
  | --- | --- |
  | Selected Model | Default model for new conversations. Change per-session with `/model`. |
  | Use Terminal | Launch Claude in terminal mode instead of graphical panel |
  | Initial Permission Mode | Controls approval prompts for file edits and commands. Defaults to `default` (ask before each action). |
  | Preferred Location | Default location: sidebar (right) or panel (new tab) |
  | Autosave | Auto-save files before Claude reads or writes them |
  | Use Ctrl+Enter to Send | Use Ctrl/Cmd+Enter instead of Enter to send prompts |
  | Enable New Conversation Shortcut | Enable Cmd/Ctrl+N to start a new conversation |
  | Respect Git Ignore | Exclude .gitignore patterns from file searches |
  | Environment Variables | Set environment variables for the Claude process. **Not recommended**—use [Claude Code settings](/docs/en/settings) instead so configuration is shared between extension and CLI. |
  | Disable Login Prompt | Skip authentication prompts (for third-party provider setups) |
  | Allow Dangerously Skip Permissions | Bypass all permission prompts. **Use with extreme caution**—recommended only for isolated sandboxes with no internet access. |
  | Claude Process Wrapper | Executable path used to launch the Claude process |
* **Claude Code settings** (`~/.claude/settings.json`): These settings are shared between the VS Code extension and the CLI. Use this file for allowed commands and directories, environment variables, hooks, and MCP servers. See the [settings documentation](/docs/en/settings) for details.

## [​](#use-third-party-providers) Use third-party providers

By default, Claude Code connects directly to Anthropic’s API. If your organization uses Amazon Bedrock, Google Vertex AI, or Microsoft Foundry to access Claude, configure the extension to use your provider instead:

1

Disable login prompt

Open the Disable Login Prompt setting and check the box.You can also open VS Code settings (`Cmd+,` on Mac or `Ctrl+,` on Windows/Linux), search for “Claude Code login”, and check **Disable Login Prompt**.

2

Configure your provider

Follow the setup guide for your provider:

* [Claude Code on Amazon Bedrock](/docs/en/amazon-bedrock)
* [Claude Code on Google Vertex AI](/docs/en/google-vertex-ai)
* [Claude Code on Microsoft Foundry](/docs/en/microsoft-foundry)

These guides cover configuring your provider in `~/.claude/settings.json`, which ensures your settings are shared between the VS Code extension and the CLI.

## [​](#vs-code-extension-vs-claude-code-cli) VS Code extension vs. Claude Code CLI

The extension doesn’t yet have full feature parity with the CLI. If you need CLI-only features, you can run `claude` directly in VS Code’s integrated terminal.

| Feature | CLI | VS Code Extension |
| --- | --- | --- |
| Slash commands | [Full set](/docs/en/slash-commands) | Subset (type `/` to see available) |
| MCP server config | Yes | No (configure via CLI, use in extension) |
| Checkpoints | Yes | Coming soon |
| `!` bash shortcut | Yes | No |
| Tab completion | Yes | No |

### [​](#run-cli-in-vs-code) Run CLI in VS Code

To use the CLI while staying in VS Code, open the integrated terminal (`` Ctrl+` `` on Windows/Linux or `` Cmd+` `` on Mac) and run `claude`. The CLI automatically integrates with your IDE for features like diff viewing and diagnostic sharing.
If using an external terminal, run `/ide` inside Claude Code to connect it to VS Code.

### [​](#switch-between-extension-and-cli) Switch between extension and CLI

The extension and CLI share the same conversation history. To continue an extension conversation in the CLI, run `claude --resume` in the terminal. This opens an interactive picker where you can search for and select your conversation.

## [​](#security-considerations) Security considerations

With auto-edit permissions enabled, Claude Code can modify VS Code configuration files (like `settings.json` or `tasks.json`) that VS Code may execute automatically. This could potentially bypass Claude Code’s normal permission prompts.
To reduce risk when working with untrusted code:

* Enable [VS Code Restricted Mode](https://code.visualstudio.com/docs/editor/workspace-trust#_restricted-mode) for untrusted workspaces
* Use manual approval mode instead of auto-accept for edits
* Review changes carefully before accepting them

## [​](#fix-common-issues) Fix common issues

### [​](#extension-won’t-install) Extension won’t install

* Ensure you have a compatible version of VS Code (1.98.0 or later)
* Check that VS Code has permission to install extensions
* Try installing directly from the Marketplace website

### [​](#spark-icon-not-visible) Spark icon not visible

There are two places the Spark icon can appear:

* **Editor Toolbar** (top-right of editor): Only visible when a file is open
* **Activity Bar** (left sidebar): Only visible after running “Claude Code: Open in Side Bar” from the Command Palette

If you don’t see the icon:

1. **Open a file**: The Editor Toolbar icon requires a file to be open—having just a folder open isn’t enough
2. **Enable the Activity Bar icon**: Run “Claude Code: Open in Side Bar” from the Command Palette once, and the icon will appear in the Activity Bar permanently
3. **Check VS Code version**: Requires 1.98.0 or higher (Help → About)
4. **Restart VS Code**: Run “Developer: Reload Window” from the command palette
5. **Disable conflicting extensions**: Temporarily disable other AI extensions (Cline, Continue, etc.)
6. **Check workspace trust**: The extension doesn’t work in Restricted Mode
7. **Use the Command Palette**: Open with `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux), then type “Claude Code: Open in Side Bar”

### [​](#spark-icon-doesn’t-stay-in-the-activity-bar) Spark icon doesn’t stay in the Activity Bar

If the Spark icon appears in the Activity Bar when you open the sidebar but doesn’t persist after you close VS Code, check that the Use Terminal setting is disabled. When terminal mode is enabled, the Activity Bar icon won’t persist between sessions.

### [​](#claude-code-never-responds) Claude Code never responds

If Claude Code isn’t responding to your prompts:

1. **Check your internet connection**: Ensure you have a stable internet connection
2. **Start a new conversation**: Try starting a fresh conversation to see if the issue persists
3. **Try the CLI**: Run `claude` from the terminal to see if you get more detailed error messages
4. **File a bug report**: If the problem continues, [file an issue on GitHub](https://github.com/anthropics/claude-code/issues) with details about the error

### [​](#standalone-cli-not-connecting-to-ide) Standalone CLI not connecting to IDE

* Ensure you’re running Claude Code from VS Code’s integrated terminal (not an external terminal)
* Ensure the CLI for your IDE variant is installed:
  + VS Code: `code` command should be available
  + Cursor: `cursor` command should be available
  + Windsurf: `windsurf` command should be available
  + VSCodium: `codium` command should be available
* If the command isn’t available, install it from the Command Palette → “Shell Command: Install ‘code’ command in PATH”

## [​](#uninstall-the-extension) Uninstall the extension

To uninstall the Claude Code extension:

1. Open the Extensions view (`Cmd+Shift+X` on Mac or `Ctrl+Shift+X` on Windows/Linux)
2. Search for “Claude Code”
3. Click **Uninstall**

To also remove extension data and reset all settings:

```
rm -rf ~/.vscode/globalStorage/anthropic.claude-code
```

For additional help, see the [troubleshooting guide](/docs/en/troubleshooting).

## [​](#next-steps) Next steps

Now that you have Claude Code set up in VS Code:

* [Explore common workflows](/docs/en/common-workflows) to get the most out of Claude Code
* [Set up MCP servers](/docs/en/mcp) to extend Claude’s capabilities with external tools. Configure servers using the CLI, then use them in the extension.
* [Configure Claude Code settings](/docs/en/settings) to customize allowed commands, hooks, and more. These settings are shared between the extension and CLI.

Was this page helpful?

YesNo

[Chrome extension (beta)](/docs/en/chrome)[JetBrains IDEs](/docs/en/jetbrains)

⌘I

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Company

[Anthropic](https://www.anthropic.com/company)[Careers](https://www.anthropic.com/careers)[Economic Futures](https://www.anthropic.com/economic-futures)[Research](https://www.anthropic.com/research)[News](https://www.anthropic.com/news)[Trust center](https://trust.anthropic.com/)[Transparency](https://www.anthropic.com/transparency)

Help and security

[Availability](https://www.anthropic.com/supported-countries)[Status](https://status.anthropic.com/)[Support center](https://support.claude.com/)

Learn

[Courses](https://www.anthropic.com/learn)[MCP connectors](https://claude.com/partners/mcp)[Customer stories](https://www.claude.com/customers)[Engineering blog](https://www.anthropic.com/engineering)[Events](https://www.anthropic.com/events)[Powered by Claude](https://claude.com/partners/powered-by-claude)[Service partners](https://claude.com/partners/services)[Startups program](https://claude.com/programs/startups)
