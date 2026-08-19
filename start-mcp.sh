#!/bin/bash
# Wrapper script to start the anti-ai-tells MCP server.
# Part of the `anti-ai-tells` OpenCode skill.
#
# Follows the same pattern as the sibling google-pse, browser-use and
# perplexity skills: a shell wrapper that prepares the environment and
# execs the real process.
#
# Usage: configure in ~/.config/opencode/opencode.json under `mcp`:
#
#   "anti-ai-tells": {
#     "type": "local",
#     "command": ["/Users/<you>/.config/opencode/skills/anti-ai-tells/start-mcp.sh"],
#     "enabled": true
#   }

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server="$script_dir/mcp_server.py"

if [ ! -f "$server" ]; then
    echo "MCP server script not found at $server" >&2
    exit 127
fi

# Prefer whatever python3 is in PATH; allow override via PYTHON3 env.
py="${PYTHON3:-python3}"
if ! command -v "$py" >/dev/null 2>&1; then
    echo "python3 not found (tried: $py)" >&2
    exit 127
fi

# Verify mcp SDK is available before spawning, to fail fast with a clear error.
if ! "$py" -c "import mcp" >/dev/null 2>&1; then
    echo "Error: Python 'mcp' package not installed for $py" >&2
    echo "Install with: $py -m pip install --user mcp" >&2
    exit 127
fi

exec "$py" "$server" "$@"
