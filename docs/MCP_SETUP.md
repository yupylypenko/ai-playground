<!-- markdownlint-disable MD013 -->
# MCP Integration Guide

This guide explains how to connect your IDE to Model Context Protocol (MCP)
servers so the ai-playground project (and the associated rag-workshop demo)
can enrich answers with real-time weather and JIRA data.

## 1. Install Node.js/npm

The published servers run with `npx`. Make sure Node.js ≥ 18 is available:

```bash
sudo apt update
sudo apt install npm
```

## 2. Configure JIRA credentials (optional but recommended)

The `jira-mcp` server needs your Atlassian Cloud site URL, email, and an API
token:

1. Sign in at <https://id.atlassian.com/manage-profile/security/api-tokens>.
2. Click **Create API token**, give it a descriptive name (e.g., “MCP
   Integration”), and copy the generated string.
3. Export the credentials before launching your IDE:

   ```bash
   export JIRA_INSTANCE_URL="https://your-domain.atlassian.net"
   export JIRA_USER_EMAIL="you@company.com"
   export JIRA_API_KEY="your-api-token"
   ```

> Tip: add the exports to your shell profile (e.g., `~/.bashrc`) so the IDE
> inherits them automatically.

## 3. Review `mcp.config.json`

Both repositories (`ai-playground` and `rag-workshop-from-scratch`) ship with an `mcp.config.json` file that enables two MCP servers:

```json
{
  "version": 1,
  "servers": {
    "weather-mcp": {
      "command": "npx",
      "args": ["-y", "@iflow-mcp/weather-mcp"],
      "workingDirectory": "."
    },
    "jira-mcp": {
      "command": "npx",
      "args": ["-y", "jira-mcp"],
      "workingDirectory": ".",
      "env": {
        "JIRA_INSTANCE_URL": "${JIRA_INSTANCE_URL}",
        "JIRA_USER_EMAIL": "${JIRA_USER_EMAIL}",
        "JIRA_API_KEY": "${JIRA_API_KEY}"
      }
    }
  },
  "prompts": {
    "enrich-with-weather": {
      "description": "Pull in real-time weather context to augment RAG answers.",
      "mcpServers": ["weather-mcp"]
    },
    "jira-issue-context": {
      "description": "Fetch issue details before answering delivery queries.",
      "mcpServers": ["jira-mcp"]
    }
  }
}
```

Place the configuration in the repository root (already committed) so
MCP-aware IDEs (Cursor, Claude Desktop, VS Code MCP extensions, etc.) can
discover it automatically.

## 4. Use the prompts

Weather enrichment example (Python pseudocode):

```python
weather_context = mcp_client.invoke_prompt(
    "enrich-with-weather",
    messages=[
        {"role": "user", "content": "What is the weather in Seattle today?"}
    ],
)
answer = f"Weather snapshot:\n{weather_context}\n\n" + rag_agent_answer
```

JIRA enrichment example:

```python
jira_context = mcp_client.invoke_prompt(
    "jira-issue-context",
    messages=[
        {
            "role": "user",
            "content": "Summarise progress on JIRA issues WEB-42 and WEB-87.",
        }
    ],
)
```

The prompts follow LangChain’s guardrail guidance by routing specialised
requests through dedicated MCP servers before combining the results with the
main RAG response.

## 5. Troubleshooting

| Issue | Fix |
| --- | --- |
| MCP server fails to start | Confirm `npx` is installed (Node.js ≥ 18). For JIRA,
ensure all three environment variables are exported. |
| IDE cannot find configuration | Ensure `mcp.config.json` lives at the
repository root or update the IDE path. |
| Unauthorized JIRA errors | Verify the site URL, email, and API token;
Atlassian may require 2FA. |
| Weather results blank | The `@iflow-mcp/weather-mcp` server only covers US
locations via the National Weather Service. |

With this configuration, every IDE session can enrich RAG responses with
real-time weather context and live JIRA data without modifying the core
application code.
<!-- markdownlint-enable MD013 -->
