# tiktoken-cli token counter

Use the maintained third-party [`samber/tiktoken-cli`](https://github.com/samber/tiktoken-cli) package for token counts. This is the standard command for all machines and file types. Do not use the Python `tiktoken` library directly or the retired `token-counter` command for routine counting.

`tiktoken-cli` counts explicitly named files regardless of extension, including LaTeX (`.tex`) and extensionless text files. It uses OpenAI-compatible `tiktoken` encodings but is a separate CLI package.

## Install

The package requires Node.js and npm. Install it globally with the user-local npm setup on each machine:

```sh
npm install --global tiktoken-cli
```

For a one-off invocation without a global install:

```sh
npx --yes tiktoken-cli path/to/file.tex
```

On the cluster, the npm prefix is under `~/.local/opt/`; its `bin` directory must be on `PATH` alongside `node`, `npm`, and `npx`. Do not commit the installed package or its generated files to this repository.

## Use

Count one or more files:

```sh
tiktoken-cli paper.tex
tiktoken-cli README.md paper.tex
```

Select the model used for tokenization:

```sh
tiktoken-cli paper.tex --model gpt-4o
```

Count a directory recursively or exclude paths:

```sh
tiktoken-cli src/
tiktoken-cli . --exclude .git/ --exclude "**/*.log"
```

Read stdin:

```sh
cat paper.tex | tiktoken-cli
```

Use `tiktoken-cli --help` for the current option list.

## Verify

```sh
command -v node
command -v npm
command -v tiktoken-cli
tiktoken-cli --version
tiktoken-cli --help
printf '\\newcommand{\\example}{text}\n' >/tmp/token-counter-smoke.tex
tiktoken-cli /tmp/token-counter-smoke.tex
```

The cluster installation was verified with `tiktoken-cli` version 0.3.0 and a `.tex` file.

## Remove

```sh
npm uninstall --global tiktoken-cli
```

Removing the CLI does not remove Node.js or npm.
