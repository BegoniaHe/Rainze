# Source: https://code.claude.com/docs/en/plugin-marketplaces

---

# Plugin marketplaces

Create and manage plugin marketplaces to distribute Claude Code extensions across teams and communities.

Plugin marketplaces are catalogs of available plugins that make it easy to discover, install, and manage Claude Code extensions. This guide shows you how to use existing marketplaces and create your own for team distribution.

## [​](#overview) Overview

A marketplace is a JSON file that lists available plugins and describes where to find them. Marketplaces provide:

* **Centralized discovery**: Browse plugins from multiple sources in one place
* **Version management**: Track and update plugin versions automatically
* **Automatic updates**: Keep plugins current with [per-marketplace auto-update settings](#auto-update-settings)
* **Team distribution**: Share required plugins across your organization
* **Flexible sources**: Support for git repositories, GitHub repos, local paths, and package managers

### [​](#prerequisites) Prerequisites

* Claude Code installed and running
* Basic familiarity with JSON file format
* For creating marketplaces: Git repository or local development environment

## [​](#add-and-use-marketplaces) Add and use marketplaces

Add marketplaces using the `/plugin marketplace` commands to access plugins from different sources:

### [​](#add-github-marketplaces) Add GitHub marketplaces

Add a GitHub repository containing .claude-plugin/marketplace.json

```
/plugin marketplace add owner/repo
```

### [​](#add-git-repositories) Add Git repositories

Add any git repository

```
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### [​](#add-local-marketplaces-for-development) Add local marketplaces for development

Add local directory containing .claude-plugin/marketplace.json

```
/plugin marketplace add ./my-marketplace
```

Add direct path to marketplace.json file

```
/plugin marketplace add ./path/to/marketplace.json
```

Add remote marketplace.json via URL

```
/plugin marketplace add https://url.of/marketplace.json
```

### [​](#install-plugins-from-marketplaces) Install plugins from marketplaces

Once you’ve added marketplaces, install plugins directly:

Install from any known marketplace

```
/plugin install plugin-name@marketplace-name
```

Browse available plugins interactively

```
/plugin
```

### [​](#verify-marketplace-installation) Verify marketplace installation

After adding a marketplace:

1. **List marketplaces**: Run `/plugin marketplace list` to confirm it’s added
2. **Browse plugins**: Use `/plugin` to see available plugins from your marketplace
3. **Test installation**: Try installing a plugin to verify the marketplace works correctly

### [​](#example-plugin-marketplace) Example plugin marketplace

Claude Code maintains a marketplace of [demo plugins](https://github.com/anthropics/claude-code/tree/main/plugins). These plugins are examples of what’s possible with the plugin system.

Add the marketplace

```
/plugin marketplace add anthropics/claude-code
```

## [​](#configure-team-marketplaces) Configure team marketplaces

Set up automatic marketplace installation for team projects by specifying required marketplaces in `.claude/settings.json`:

```
{
  "extraKnownMarketplaces": {
    "team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    },
    "project-specific": {
      "source": {
        "source": "git",
        "url": "https://git.company.com/project-plugins.git"
      }
    }
  }
}
```

When team members trust the repository folder, Claude Code automatically installs these marketplaces and any plugins specified in the `enabledPlugins` field.

## [​](#enterprise-marketplace-restrictions) Enterprise marketplace restrictions

For organizations requiring strict control over plugin sources, enterprise administrators can restrict which plugin marketplaces users are allowed to add using the `strictKnownMarketplaces` setting in managed settings.
**Managed settings file locations**:

* **macOS**: `/Library/Application Support/ClaudeCode/managed-settings.json`
* **Linux and WSL**: `/etc/claude-code/managed-settings.json`
* **Windows**: `C:\ProgramData\ClaudeCode\managed-settings.json`

**Restriction behavior**:
When `strictKnownMarketplaces` is configured in managed settings:

* **Undefined** (default): No restrictions - users can add any marketplace
* **Empty array `[]`**: Complete lockdown - users cannot add any new marketplaces
* **List of sources**: Users can only add marketplaces that match the allowlist exactly

**Basic examples**:
Disable all marketplace additions:

```
{
  "strictKnownMarketplaces": []
}
```

Allow specific marketplaces only:

```
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "company/approved-plugins"
    },
    {
      "source": "github",
      "repo": "company/security-tools",
      "ref": "v2.0"
    },
    {
      "source": "url",
      "url": "https://internal.company.com/plugins/marketplace.json"
    }
  ]
}
```

**Key characteristics**:

* Enforced BEFORE network/filesystem operations
* Uses exact matching (including optional `ref` and `path` fields for git sources)
* Cannot be overridden by user or project settings
* Only affects adding NEW marketplaces (previously installed marketplaces still work)

See [strictKnownMarketplaces reference](/docs/en/settings#strictknownmarketplaces) for complete configuration details, including all six supported source types, exact matching rules, and comparison with `extraKnownMarketplaces`.

---

## [​](#create-your-own-marketplace) Create your own marketplace

Build and distribute custom plugin collections for your team or community.

### [​](#prerequisites-for-marketplace-creation) Prerequisites for marketplace creation

* Git repository (GitHub, GitLab, or other git hosting)
* Understanding of JSON file format
* One or more plugins to distribute

### [​](#create-the-marketplace-file) Create the marketplace file

Create `.claude-plugin/marketplace.json` in your repository root:

```
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "[email protected]"
  },
  "plugins": [
    {
      "name": "code-formatter",
      "source": "./plugins/formatter",
      "description": "Automatic code formatting on save",
      "version": "2.1.0",
      "author": {
        "name": "DevTools Team"
      }
    },
    {
      "name": "deployment-tools",
      "source": {
        "source": "github",
        "repo": "company/deploy-plugin"
      },
      "description": "Deployment automation tools"
    }
  ]
}
```

### [​](#marketplace-schema) Marketplace schema

#### [​](#required-fields) Required fields

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Marketplace identifier (kebab-case, no spaces) |
| `owner` | object | Marketplace maintainer information |
| `plugins` | array | List of available plugins |

#### [​](#optional-metadata) Optional metadata

| Field | Type | Description |
| --- | --- | --- |
| `metadata.description` | string | Brief marketplace description |
| `metadata.version` | string | Marketplace version |
| `metadata.pluginRoot` | string | Base path for relative plugin sources |

### [​](#plugin-entries) Plugin entries

Plugin entries are based on the *plugin manifest schema* (with all fields made
optional) plus marketplace-specific fields (`source`, `category`, `tags`,
`strict`), with `name` being required.

**Required fields:**

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Plugin identifier (kebab-case, no spaces) |
| `source` | string|object | Where to fetch the plugin from |

#### [​](#optional-plugin-fields) Optional plugin fields

**Standard metadata fields:**

| Field | Type | Description |
| --- | --- | --- |
| `description` | string | Brief plugin description |
| `version` | string | Plugin version |
| `author` | object | Plugin author information |
| `homepage` | string | Plugin homepage or documentation URL |
| `repository` | string | Source code repository URL |
| `license` | string | SPDX license identifier (for example, MIT, Apache-2.0) |
| `keywords` | array | Tags for plugin discovery and categorization |
| `category` | string | Plugin category for organization |
| `tags` | array | Tags for searchability |
| `strict` | boolean | Require plugin.json in plugin folder (default: true) 1 |

**Component configuration fields:**

| Field | Type | Description |
| --- | --- | --- |
| `commands` | string|array | Custom paths to command files or directories |
| `agents` | string|array | Custom paths to agent files |
| `hooks` | string|object | Custom hooks configuration or path to hooks file |
| `mcpServers` | string|object | MCP server configurations or path to MCP config |

*1 - When `strict: true` (default), the plugin must include a `plugin.json` manifest file, and marketplace fields supplement those values. When `strict: false`, the plugin.json is optional. If it’s missing, the marketplace entry serves as the complete plugin manifest.*

### [​](#plugin-sources) Plugin sources

#### [​](#relative-paths) Relative paths

For plugins in the same repository:

```
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin"
}
```

#### [​](#github-repositories) GitHub repositories

```
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo"
  }
}
```

#### [​](#git-repositories) Git repositories

```
{
  "name": "git-plugin",
  "source": {
    "source": "url",
    "url": "https://gitlab.com/team/plugin.git"
  }
}
```

#### [​](#advanced-plugin-entries) Advanced plugin entries

Plugin entries can override default component locations and provide additional metadata. Note that `${CLAUDE_PLUGIN_ROOT}` is an environment variable that resolves to the plugin’s installation directory (for details see [Environment variables](/docs/en/plugins-reference#environment-variables)):

```
{
  "name": "enterprise-tools",
  "source": {
    "source": "github",
    "repo": "company/enterprise-plugin"
  },
  "description": "Enterprise workflow automation tools",
  "version": "2.1.0",
  "author": {
    "name": "Enterprise Team",
    "email": "[email protected]"
  },
  "homepage": "https://docs.company.com/plugins/enterprise-tools",
  "repository": "https://github.com/company/enterprise-plugin",
  "license": "MIT",
  "keywords": ["enterprise", "workflow", "automation"],
  "category": "productivity",
  "commands": [
    "./commands/core/",
    "./commands/enterprise/",
    "./commands/experimental/preview.md"
  ],
  "agents": ["./agents/security-reviewer.md", "./agents/compliance-checker.md"],
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
          }
        ]
      }
    ]
  },
  "mcpServers": {
    "enterprise-db": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  },
  "strict": false
}
```

**Schema relationship**: Plugin entries use the plugin manifest schema with
all fields made optional, plus marketplace-specific fields (`source`,
`strict`, `category`, `tags`). This means any field valid in a `plugin.json`
file can also be used in a marketplace entry. When `strict: false`, the
marketplace entry serves as the complete plugin manifest if no `plugin.json`
exists. When `strict: true` (default), marketplace fields supplement the
plugin’s own manifest file.

---

## [​](#host-and-distribute-marketplaces) Host and distribute marketplaces

Choose the best hosting strategy for your plugin distribution needs.

### [​](#host-on-github-recommended) Host on GitHub (recommended)

GitHub provides the easiest distribution method:

1. **Create a repository**: Set up a new repository for your marketplace
2. **Add marketplace file**: Create `.claude-plugin/marketplace.json` with your plugin definitions
3. **Share with teams**: Team members add with `/plugin marketplace add owner/repo`

**Benefits**: Built-in version control, issue tracking, and team collaboration features.

### [​](#host-on-other-git-services) Host on other git services

Any git hosting service works for marketplace distribution, using a URL to an arbitrary git repository.
For example, using GitLab:

```
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### [​](#use-local-marketplaces-for-development) Use local marketplaces for development

Test your marketplace locally before distribution:

Add local marketplace for testing

```
/plugin marketplace add ./my-local-marketplace
```

Test plugin installation

```
/plugin install test-plugin@my-local-marketplace
```

## [​](#manage-marketplace-operations) Manage marketplace operations

### [​](#list-known-marketplaces) List known marketplaces

List all configured marketplaces

```
/plugin marketplace list
```

Shows all configured marketplaces with their sources and status.

### [​](#update-marketplace-metadata) Update marketplace metadata

Refresh marketplace metadata

```
/plugin marketplace update marketplace-name
```

Refreshes plugin listings and metadata from the marketplace source.

### [​](#remove-a-marketplace) Remove a marketplace

Remove a marketplace

```
/plugin marketplace remove marketplace-name
```

Removes the marketplace from your configuration.

Removing a marketplace will uninstall any plugins you installed from it.

---

## [​](#auto-update-settings) Auto-update settings

Claude Code can automatically update marketplaces and their installed plugins at startup. This keeps your plugins current without manual intervention.

### [​](#how-auto-update-works) How auto-update works

When auto-update is enabled for a marketplace:

1. **Marketplace refresh**: Claude Code pulls the latest marketplace data (git pull or re-download)
2. **Plugin updates**: Installed plugins from that marketplace are updated to their latest versions
3. **Notification**: If any plugins were updated, you’ll see a notification suggesting a restart

### [​](#configure-auto-update-per-marketplace) Configure auto-update per marketplace

Toggle auto-update for individual marketplaces through the UI:

1. Run `/plugin` to open the plugin manager
2. Select **Marketplaces**
3. Choose a marketplace from the list
4. Select **Enable auto-update** or **Disable auto-update**

Official Anthropic marketplaces have auto-update enabled by default. You can disable this if you prefer manual updates.

### [​](#auto-update-behavior) Auto-update behavior

| Marketplace type | Default behavior |
| --- | --- |
| Official Anthropic marketplaces | Auto-update enabled |
| Third-party marketplaces | Auto-update disabled |
| Local development marketplaces | Auto-update disabled |

### [​](#disable-auto-update-globally) Disable auto-update globally

To disable all automatic updates (both Claude Code and plugins), set the `DISABLE_AUTOUPDATER` environment variable. See [Auto updates](/docs/en/setup#auto-updates) for details.
When auto-updates are disabled globally:

* No marketplaces or plugins will auto-update
* The auto-update toggle is hidden in the UI
* You can still manually update using `/plugin marketplace update`

---

## [​](#troubleshooting-marketplaces) Troubleshooting marketplaces

### [​](#common-marketplace-issues) Common marketplace issues

#### [​](#marketplace-not-loading) Marketplace not loading

**Symptoms**: Can’t add marketplace or see plugins from it
**Solutions**:

* Verify the marketplace URL is accessible
* Check that `.claude-plugin/marketplace.json` exists at the specified path
* Ensure JSON syntax is valid using `claude plugin validate`
* For private repositories, confirm you have access permissions

#### [​](#plugin-installation-failures) Plugin installation failures

**Symptoms**: Marketplace appears but plugin installation fails
**Solutions**:

* Verify plugin source URLs are accessible
* Check that plugin directories contain required files
* For GitHub sources, ensure repositories are public or you have access
* Test plugin sources manually by cloning/downloading

### [​](#validation-and-testing) Validation and testing

Test your marketplace before sharing:

Validate marketplace JSON syntax

```
claude plugin validate .
```

Add marketplace for testing

```
/plugin marketplace add ./path/to/marketplace
```

Install test plugin

```
/plugin install test-plugin@marketplace-name
```

For complete plugin testing workflows, see [Test your plugins locally](/docs/en/plugins#test-your-plugins-locally). For technical troubleshooting, see [Plugins reference](/docs/en/plugins-reference).

---

## [​](#next-steps) Next steps

### [​](#for-marketplace-users) For marketplace users

* **Discover community marketplaces**: Search GitHub for Claude Code plugin collections
* **Contribute feedback**: Report issues and suggest improvements to marketplace maintainers
* **Share useful marketplaces**: Help your team discover valuable plugin collections

### [​](#for-marketplace-creators) For marketplace creators

* **Build plugin collections**: Create themed marketplace around specific use cases
* **Establish versioning**: Implement clear versioning and update policies
* **Community engagement**: Gather feedback and maintain active marketplace communities
* **Documentation**: Provide clear README files explaining your marketplace contents

### [​](#for-organizations) For organizations

* **Private marketplaces**: Set up internal marketplaces for proprietary tools
* **Governance policies**: Establish guidelines for plugin approval and security review
* **Training resources**: Help teams discover and adopt useful plugins effectively

## [​](#see-also) See also

* [Plugins](/docs/en/plugins) - Installing and using plugins
* [Plugins reference](/docs/en/plugins-reference) - Complete technical specifications and schemas
* [Plugin development](/docs/en/plugins#develop-more-complex-plugins) - Creating your own plugins
* [Settings](/docs/en/settings#plugin-configuration) - Plugin configuration options
* [strictKnownMarketplaces reference](/docs/en/settings#strictknownmarketplaces) - Complete configuration reference for enterprise marketplace restrictions

Was this page helpful?

YesNo

[Analytics](/docs/en/analytics)

⌘I

[x](https://x.com/AnthropicAI)[linkedin](https://www.linkedin.com/company/anthropicresearch)

Company

[Anthropic](https://www.anthropic.com/company)[Careers](https://www.anthropic.com/careers)[Economic Futures](https://www.anthropic.com/economic-futures)[Research](https://www.anthropic.com/research)[News](https://www.anthropic.com/news)[Trust center](https://trust.anthropic.com/)[Transparency](https://www.anthropic.com/transparency)

Help and security

[Availability](https://www.anthropic.com/supported-countries)[Status](https://status.anthropic.com/)[Support center](https://support.claude.com/)

Learn

[Courses](https://www.anthropic.com/learn)[MCP connectors](https://claude.com/partners/mcp)[Customer stories](https://www.claude.com/customers)[Engineering blog](https://www.anthropic.com/engineering)[Events](https://www.anthropic.com/events)[Powered by Claude](https://claude.com/partners/powered-by-claude)[Service partners](https://claude.com/partners/services)[Startups program](https://claude.com/programs/startups)
