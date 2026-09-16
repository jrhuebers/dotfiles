# Pi simple web tools

`pi-simple-web-tools` is the Pi extension used for compact web access inside
agents. It is currently listed in both the cluster and personal Pi profiles;
whether it is usable on a cluster depends on that cluster's network policy and
its separately configured user credential.

It exposes exactly two tools:

- `web_search` — Exa-backed web search. Requires an Exa API key.
- `fetch_content` — fetch a web page or PDF and return readable Markdown/text. Large outputs are written to a temp file and returned with a preview/path.

The package source is `jillesme/pi-simple-web-tools`; the installed npm package name is `pi-simple-web-tools`.

## Current personal-device setup

On the Fedora ThinkPad, this is installed as a Pi npm package. The package is
also present in the cluster Pi settings snapshot, but it is not a substitute
for checking cluster outbound-network policy:

```sh
pi install npm:pi-simple-web-tools
```

Pi installs npm extension packages under:

```sh
~/.pi/agent/npm/node_modules/pi-simple-web-tools
```

The laptop currently has package version `0.1.0` installed.

Authentication is through a per-user config file, not an exported shell variable:

```sh
~/.pi/web-tools.json
```

That file is secret-bearing and must not be copied into this repository, printed, committed, or shared.

## Install on a new machine

Prerequisites:

- Pi CLI is installed and working.
- The user has an Exa API key from <https://exa.ai>.
- Run the commands as the target user, not with `sudo`.

Install the extension:

```sh
pi install npm:pi-simple-web-tools
```

Create the Exa config file securely:

```bash
mkdir -p ~/.pi
read -rsp 'Exa API key: ' EXA_API_KEY_INPUT; printf '\n'
export EXA_API_KEY_INPUT
python3 - <<'PY'
import json
import os
from pathlib import Path

key = os.environ.get('EXA_API_KEY_INPUT')
if not key:
    raise SystemExit('EXA_API_KEY_INPUT was empty')

path = Path.home() / '.pi' / 'web-tools.json'
text = json.dumps({'exaApiKey': key}, indent=2) + '\n'
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(text)
path.chmod(0o600)
print(f'wrote {path}')
PY
unset EXA_API_KEY_INPUT
```

Alternative authentication is to export `EXA_API_KEY` in the environment that launches Pi, but the laptop setup uses `~/.pi/web-tools.json` because it is explicit and user-scoped.

Config precedence:

1. `EXA_API_KEY` environment variable
2. `exaApiKey` in `~/.pi/web-tools.json`

If the config file must live somewhere else, set `PI_WEB_TOOLS_CONFIG` to the alternate path in the environment that launches Pi.

After installing or changing config, restart Pi or run `/reload` inside the Pi session.

## Optional SSRF allow ranges

The config may also contain an SSRF allowlist for unusual proxy setups that resolve public domains into reserved/fake IP ranges:

```json
{
  "exaApiKey": "exa-...",
  "ssrf": { "allowRanges": ["198.18.0.0/15"] }
}
```

Do not add `ssrf.allowRanges` unless the machine actually needs it. The laptop does not document a required allow range for normal operation.

## Verify installation

Check that the package is installed:

```sh
pi list
node -e "const os=require('os'); const p=os.homedir()+'/.pi/agent/npm/node_modules/pi-simple-web-tools/package.json'; console.log(require(p).version)"
```

Check that config exists without revealing the key:

```sh
test -f ~/.pi/web-tools.json && stat -c '%n %a %s bytes' ~/.pi/web-tools.json
python3 - <<'PY'
import json
from pathlib import Path
path = Path.home() / '.pi' / 'web-tools.json'
data = json.loads(path.read_text())
print('exaApiKey configured:', bool(data.get('exaApiKey')))
print('ssrf configured:', 'ssrf' in data)
PY
```

Inside a Pi session, verify the tools by asking the agent to run:

```text
Use web_search for "Exa API documentation" with 1 result.
Use fetch_content on https://example.com/.
```

Expected result: `web_search` returns ranked Exa results with URLs/snippets, and `fetch_content` returns readable Markdown/text.

## Tool behavior notes for agents

- Prefer `web_search` with 2–4 varied queries for research coverage.
- Use `fetch_content` on selected URLs returned by search.
- `fetch_content` asks for Markdown first, then falls back through HTML readability extraction and PDF text extraction.
- Large fetched documents are saved under `$TMPDIR/pi-web-tools/`; read those paths in slices instead of loading the whole file into context.
- Do not fetch, print, or commit `~/.pi/web-tools.json` or any API key.

## Troubleshooting

If `web_search` says the Exa key is missing:

1. Confirm `~/.pi/web-tools.json` exists and has mode `600`.
2. Confirm it contains an `exaApiKey` field without printing the value.
3. Confirm Pi was restarted or `/reload` was run after writing the file.
4. Confirm no stale `PI_WEB_TOOLS_CONFIG` points at another file.
5. If using environment auth instead, confirm `EXA_API_KEY` is exported in the same environment that launched Pi.

If Pi reports duplicate tool names, another extension is registering `web_search` or `fetch_content`. Disable the duplicate extension entry in `~/.pi/agent/settings.json`, or configure that package with no exported tools if it supports extension filtering.

## Removal

Remove or disable the package from Pi with the corresponding Pi package-management command for the installed Pi version, then restart Pi or run `/reload`.

If the machine should no longer use Exa, remove the secret config file too:

```sh
rm ~/.pi/web-tools.json
```
