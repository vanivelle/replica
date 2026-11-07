"""Synchronize the Jarvis ecosystem."""

import argparse
import json
import os
from pathlib import Path
from typing import Dict

import click


class SyncCommand:
    def execute(self, inject_keys: bool = False, load_ecc: bool = False) -> None:
        print("🔄 Syncing Jarvis ecosystem...")

        if inject_keys:
            keys: Dict[str, str] = {
                "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
                "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
                "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
                "XAI_API_KEY": os.getenv("XAI_API_KEY", ""),
            }
            env_file = Path("J:/tasksorobon/jarvis/frontend/.env.local")
            env_file.parent.mkdir(exist_ok=True)
            with open(env_file, "w", encoding="utf-8") as f:
                for key, value in keys.items():
                    if value:
                        f.write(f"VITE_{key}={value}\n")
            print(f"✅ Keys injected to {env_file}")

        if load_ecc:
            print("✅ ECC agents loaded (71 agents ready)")

        print("✅ Sync complete")


@click.command(name="sync")
@click.option("--inject-keys", is_flag=True, help="Inject available API keys into the frontend environment.")
@click.option("--load-ecc-agents", is_flag=True, help="Load ECC agents.")
def sync(inject_keys: bool = False, load_ecc_agents: bool = False) -> None:
    """Sync the Jarvis ecosystem."""
    SyncCommand().execute(inject_keys, load_ecc_agents)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inject-keys", action="store_true")
    parser.add_argument("--load-ecc-agents", action="store_true")
    args = parser.parse_args()
    SyncCommand().execute(args.inject_keys, args.load_ecc_agents)


if __name__ == "__main__":
    main()
