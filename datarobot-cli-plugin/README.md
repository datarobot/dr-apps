# DataRobot CLI Plugin: dr-apps

This directory contains the CLI plugin wrapper scripts for the `dr-apps` tool.

## Building the Plugin

To build the CLI plugin package:

```bash
make cli-plugin
```

This will:
1. Build a Python wheel from the repository
2. Find the wheel and extract the version from its filename
3. Create a `dist/plugin-staging/` directory with:
   - The wheel file
   - Platform-specific wrapper scripts (`dr-apps.sh` and `dr-apps.ps1`)
   - A `manifest.json` with the wheel version

## Publishing a New Version

To publish a new version of the plugin:

1. **Update the version** in `setup.cfg` (e.g., `version = 11.2.0`)

2. **Build the plugin**:
   ```bash
   make clean
   make cli-plugin
   ```

3. **Clone or checkout the DataRobot CLI repository** where the plugin index is maintained:
   ```bash
   git clone <cli-repo-url>
   cd <cli-repo>
   ```

4. **Publish the plugin** from your dr-apps directory:
   ```bash
   make publish-cli-plugin PLUGIN_PUBLISH_FLAGS="--plugins-dir /path/to/cli-repo/docs/plugins --index /path/to/cli-repo/docs/plugins/index.json"
   ```

5. **Commit and push the changes** in the CLI repo:
   ```bash
   cd /path/to/cli-repo
   git add docs/plugins/
   git commit -m "Add dr-apps plugin v11.2.0"
   git push
   ```

The plugin will be available at `docs/plugins/index.json` in the CLI repository.

## Alternative: Manual Packaging

If you need more control, you can use the individual commands:

```bash
# Build the plugin
make cli-plugin

# Package it (creates a .tar.xz archive)
make package-cli-plugin PLUGIN_PACKAGE_FLAGS="-o /path/to/output"

# Publish to the index
make publish-cli-plugin PLUGIN_PUBLISH_FLAGS="--plugins-dir /path/to/plugins --index /path/to/index.json"
```

## Plugin Structure

The generated plugin directory contains:
- `dr-apps.sh` - Unix/Linux/macOS wrapper script
- `dr-apps.ps1` - Windows PowerShell wrapper script
- `drapps-{version}-py3-none-any.whl` - Python wheel package
- `manifest.json` - Plugin metadata

## How It Works

The wrapper scripts use `uv` to execute the bundled wheel package. The scripts:
- Check for `uv` availability and provide installation instructions if missing
- Handle the `--dr-plugin-manifest` flag for CLI integration
- Use their own directory (`$SCRIPT_DIR`) to locate the wheel file
- Execute `drapps` via `uv run --with <wheel-path>`

## Requirements

- `uv` must be installed to use the plugin
- Python 3.9+ is required
