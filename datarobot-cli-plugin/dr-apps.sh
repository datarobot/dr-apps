#!/usr/bin/env bash
# dr-apps - DataRobot custom application hosting plugin
# This script wraps the drapps Python package using uv

set -euo pipefail

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. Please install it first:" >&2
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

# Handle --dr-plugin-manifest flag for CLI integration
if [[ "${{1:-}}" == "--dr-plugin-manifest" ]]; then
    cat << 'EOF'
{{"name":"{plugin_name}","version":"{version}","description":"{plugin_description}"}}
EOF
    exit 0
fi

# Execute drapps via uv with the bundled wheel package
exec uv run --with "$SCRIPT_DIR/{wheel_name}" drapps "$@"
