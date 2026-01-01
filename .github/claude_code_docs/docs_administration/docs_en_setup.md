# Source: https://code.claude.com/docs/en/setup

---

# Set up Claude Code

Install, authenticate, and start using Claude Code on your development machine.

## [​](#system-requirements) System requirements

* **Operating Systems**: macOS 10.15+, Ubuntu 20.04+/Debian 10+, or Windows 10+ (with WSL 1, WSL 2, or Git for Windows)
* **Hardware**: 4 GB+ RAM
* **Software**: [Node.js 18+](https://nodejs.org/en/download) (only required for npm installation)
* **Network**: Internet connection required for authentication and AI processing
* **Shell**: Works best in Bash, Zsh or Fish
* **Location**: [Anthropic supported countries](https://www.anthropic.com/supported-countries)

### [​](#additional-dependencies) Additional dependencies

* **ripgrep**: Usually included with Claude Code. If search fails, see [search troubleshooting](/docs/en/troubleshooting#search-and-discovery-issues).

## [​](#standard-installation) Standard installation

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

Some users may be automatically migrated to an improved installation method.

After the installation process completes, navigate to your project and start Claude Code:

```
cd your-awesome-project
claude
```

Claude Code offers the following authentication options:

1. **Claude Console**: The default option. Connect through the Claude Console and complete the OAuth process. Requires active billing in the [Anthropic console](https://console.anthropic.com). A “Claude Code” workspace is automatically created for usage tracking and cost management. You can’t create API keys for the Claude Code workspace; it’s dedicated exclusively for Claude Code usage.
2. **Claude App (with Pro or Max plan)**: Subscribe to Claude’s [Pro or Max plan](https://claude.com/pricing) for a unified subscription that includes both Claude Code and the web interface. Get more value at the same price point while managing your account in one place. Log in with your Claude.ai account. During launch, choose the option that matches your subscription type.
3. **Enterprise platforms**: Configure Claude Code to use [Amazon Bedrock, Google Vertex AI, or Microsoft Foundry](/docs/en/third-party-integrations) for enterprise deployments with your existing cloud infrastructure.

Claude Code securely stores your credentials. See [Credential Management](/docs/en/iam#credential-management) for details.

## [​](#windows-setup) Windows setup

**Option 1: Claude Code within WSL**

* Both WSL 1 and WSL 2 are supported

**Option 2: Claude Code on native Windows with Git Bash**

* Requires [Git for Windows](https://git-scm.com/downloads/win)
* For portable Git installations, specify the path to your `bash.exe`:

  ```
  $env:CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"
  ```

## [​](#alternative-installation-methods) Alternative installation methods

Claude Code offers multiple installation methods to suit different environments.
If you encounter any issues during installation, consult the [troubleshooting guide](/docs/en/troubleshooting#linux-permission-issues).

Run `claude doctor` after installation to check your installation type and version.

### [​](#native-installation-options) Native installation options

The native installation is the recommended method and offers several benefits:

* One self-contained executable
* No Node.js dependency
* Improved auto-updater stability

If you have an existing installation of Claude Code, use `claude install` to migrate to the native binary installation.
For advanced installation options with the native installer:
**macOS, Linux, WSL:**

```

# Install stable version (default)
curl -fsSL https://claude.ai/install.sh | bash

# Install latest version
curl -fsSL https://claude.ai/install.sh | bash -s latest

# Install specific version number
curl -fsSL https://claude.ai/install.sh | bash -s 1.0.58
```

**Alpine Linux and other musl/uClibc-based distributions**: The native build requires `libgcc`, `libstdc++`, and `ripgrep`. For Alpine: `apk add libgcc libstdc++ ripgrep`. Set `USE_BUILTIN_RIPGREP=0`.

**Windows PowerShell:**

```

# Install stable version (default)
irm https://claude.ai/install.ps1 | iex

# Install latest version
& ([scriptblock]::Create((irm https://claude.ai/install.ps1))) latest

# Install specific version number
& ([scriptblock]::Create((irm https://claude.ai/install.ps1))) 1.0.58
```

**Windows CMD:**

```
REM Install stable version (default)
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

REM Install latest version
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd latest && del install.cmd

REM Install specific version number
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd 1.0.58 && del install.cmd
```

Make sure that you remove any outdated aliases or symlinks before installing.

**Binary integrity and code signing**

* SHA256 checksums for all platforms are published in the release manifests, currently located at `https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/{VERSION}/manifest.json` (example: replace `{VERSION}` with `2.0.30`)
* Signed binaries are distributed for the following platforms:
  + macOS: Signed by “Anthropic PBC” and notarized by Apple
  + Windows: Signed by “Anthropic, PBC”

### [​](#npm-installation) NPM installation

For environments where NPM is preferred or required:

```
npm install -g @anthropic-ai/claude-code
```

Do NOT use `sudo npm install -g` as this can lead to permission issues and security risks.
If you encounter permission errors, see [configure Claude Code](/docs/en/troubleshooting#linux-permission-issues) for recommended solutions.

## [​](#running-on-aws-or-gcp) Running on AWS or GCP

By default, Claude Code uses the Claude API.
For details on running Claude Code on AWS or GCP, see [third-party integrations](/docs/en/third-party-integrations).

## [​](#update-claude-code) Update Claude Code

### [​](#auto-updates) Auto updates

Claude Code automatically keeps itself up to date to ensure you have the latest features and security fixes.

* **Update checks**: Performed on startup and periodically while running
* **Update process**: Downloads and installs automatically in the background
* **Notifications**: You’ll see a notification when updates are installed
* **Applying updates**: Updates take effect the next time you start Claude Code

**Disable auto-updates:**
Set the `DISABLE_AUTOUPDATER` environment variable in your shell or [settings.json file](/docs/en/settings):

```
export DISABLE_AUTOUPDATER=1
```

### [​](#update-manually) Update manually

```
claude update
```

## [​](#uninstall-claude-code) Uninstall Claude Code

If you need to uninstall Claude Code, follow the instructions for your installation method.

### [​](#native-installation) Native installation

Remove the Claude Code binary and symlink:
**macOS, Linux, WSL:**

```
rm -f ~/.local/bin/claude
rm -rf ~/.claude-code
```

**Windows PowerShell:**

```
Remove-Item -Path "$env:LOCALAPPDATA\Programs\claude-code" -Recurse -Force
Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\WindowsApps\claude.exe" -Force
```

**Windows CMD:**

```
rmdir /s /q "%LOCALAPPDATA%\Programs\claude-code"
del "%LOCALAPPDATA%\Microsoft\WindowsApps\claude.exe"
```

### [​](#homebrew-installation) Homebrew installation

```
brew uninstall --cask claude-code
```

### [​](#npm-installation-2) NPM installation

```
npm uninstall -g @anthropic-ai/claude-code
```

### [​](#clean-up-configuration-files-optional) Clean up configuration files (optional)

Removing configuration files will delete all your settings, allowed tools, MCP server configurations, and session history.

To remove Claude Code settings and cached data:
**macOS, Linux, WSL:**

```

# Remove user settings and state
rm -rf ~/.claude
rm ~/.claude.json

# Remove project-specific settings (run from your project directory)
rm -rf .claude
rm -f .mcp.json
```

**Windows PowerShell:**

```

# Remove user settings and state
Remove-Item -Path "$env:USERPROFILE\.claude" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.claude.json" -Force

# Remove project-specific settings (run from your project directory)
Remove-Item -Path ".claude" -Recurse -Force
Remove-Item -Path ".mcp.json" -Force
```

**Windows CMD:**

```
REM Remove user settings and state
rmdir /s /q "%USERPROFILE%\.claude"
del "%USERPROFILE%\.claude.json"

REM Remove project-specific settings (run from your project directory)
rmdir /s /q ".claude"
del ".mcp.json"
```

Was this page helpful?

YesNo

[Identity and Access Management](/docs/en/iam)

⌘I

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Company

[Anthropic](https://www.anthropic.com/company)[Careers](https://www.anthropic.com/careers)[Economic Futures](https://www.anthropic.com/economic-futures)[Research](https://www.anthropic.com/research)[News](https://www.anthropic.com/news)[Trust center](https://trust.anthropic.com/)[Transparency](https://www.anthropic.com/transparency)

Help and security

[Availability](https://www.anthropic.com/supported-countries)[Status](https://status.anthropic.com/)[Support center](https://support.claude.com/)

Learn

[Courses](https://www.anthropic.com/learn)[MCP connectors](https://claude.com/partners/mcp)[Customer stories](https://www.claude.com/customers)[Engineering blog](https://www.anthropic.com/engineering)[Events](https://www.anthropic.com/events)[Powered by Claude](https://claude.com/partners/powered-by-claude)[Service partners](https://claude.com/partners/services)[Startups program](https://claude.com/programs/startups)
