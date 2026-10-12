<div align="center">

<img src="src/ebisu/cli/assets/ebisu.png" alt="Ebisu logo" width="220" />

# Ebisu

**An open-source AI coding agent harness built for local LLMs.**

![Python](https://img.shields.io/badge/python-3.13%2B-3776AB?logo=python&logoColor=white)
![TUI](https://img.shields.io/badge/interface-terminal%20UI-F5C518)
![Status](https://img.shields.io/badge/status-early%20development-E8321E)

</div>

---

## About

Ebisu is a coding agent harness designed to run against models on your own machine. No cloud account required, and your code stays local.

It ships with a terminal user interface built on [Textual](https://github.com/Textualize/textual) and [Rich](https://github.com/Textualize/rich), and detects your system and GPU so it can fit local models to your hardware.

> Ebisu is in early development (`v0.1.0`). Expect rough edges and breaking changes.

## Installation

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Ananthannn/Ebisu.git
cd Ebisu
uv sync
```

## Usage

```bash
uv run ebisu
```

## Project layout

```
src/ebisu/
├── __init__.py      # entry point (`ebisu` command)
└── cli/             # terminal UI, system/GPU info, logo rendering
    └── assets/      # logo and other assets
```

## Built with

[Textual](https://github.com/Textualize/textual) · [Rich](https://github.com/Textualize/rich) · [psutil](https://github.com/giampaolo/psutil) · [Pillow](https://python-pillow.org/)

## Contributing

Issues and pull requests are welcome.
