from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml


ALLOWED_PROVIDERS = {"openai", "gemini"}
DEFAULT_EMBEDDING_SETTINGS = {
    "provider": "openai",
    "model": "text-embedding-ada-002",
    "api_base": "https://api.openai.com/v1",
    "api_key": "$OPENAI_API_KEY",
    "timeout": 120.0,
    "max_retries": 1,
}


def enforce(config: Mapping[str, Any]) -> tuple[dict[str, Any], bool]:
    config = dict(config)
    changed = False

    embeddings = config.get("embeddings")
    if not isinstance(embeddings, dict):
        embeddings = {}
        config["embeddings"] = embeddings
        changed = True

    provider = embeddings.get("provider")
    if provider not in ALLOWED_PROVIDERS:
        embeddings["provider"] = DEFAULT_EMBEDDING_SETTINGS["provider"]
        changed = True

    for key, default in DEFAULT_EMBEDDING_SETTINGS.items():
        if key == "provider":
            continue
        if key not in embeddings:
            embeddings[key] = default
            changed = True

    rerank = config.get("rerank")
    if not isinstance(rerank, dict):
        rerank = {}
        config["rerank"] = rerank
        changed = True

    if rerank.get("enabled") is not False:
        rerank["enabled"] = False
        changed = True

    if rerank.get("mode") != "off":
        rerank["mode"] = "off"
        changed = True

    return config, changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Force cloud embeddings + disable rerank")
    parser.add_argument("--config", type=Path, required=True, help="Path to config.yaml")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.config.exists():
        print(f"✗ config file not found: {args.config}", file=sys.stderr)
        return 2

    raw = args.config.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    new_config, changed = enforce(data)

    if not changed:
        print("✓ config already enforces cloud embeddings and disabled rerank.")
        return 0

    args.config.write_text(yaml.safe_dump(new_config, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"✓ Updated {args.config.name}: embeddings -> {new_config['embeddings']['provider']}, rerank disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
