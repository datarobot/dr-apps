# dr-apps - DataRobot custom application hosting plugin
# This script wraps the drapps Python package using uv

$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Handle --dr-plugin-manifest flag for CLI integration
if ($args.Count -gt 0 -and $args[0] -eq "--dr-plugin-manifest") {{
    Write-Output '{{\"name\":\"{plugin_name}\",\"version\":\"{version}\",\"description\":\"{plugin_description}\"}}'
    exit 0
}}

# Check if uv is available
$uvPath = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvPath) {{
    Write-Error "Error: 'uv' is not installed. Please install it first:"
    Write-Error "  powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    exit 1
}}

# Execute drapps via uv with the bundled wheel package
& uv run --with "$ScriptDir\{wheel_name}" drapps @args
exit $LASTEXITCODE
