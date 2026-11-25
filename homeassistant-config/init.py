"""Ensure the managed Recorder include exists before Home Assistant starts."""
import os
import sys
import tempfile
from pathlib import Path

import yaml

DEFAULT_CONFIG = """# Loads default set of integrations. Do not remove.
default_config:

# Load frontend themes from the themes folder
frontend:
  themes: !include_dir_merge_named themes

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
"""
INCLUDE = "recorder: !include recorder.yaml"


def ensure_recorder(config_dir):
    config = config_dir / "configuration.yaml"
    if not config.exists():
        for name, contents in {
            "automations.yaml": "[]\n",
            "scripts.yaml": "{}\n",
            "scenes.yaml": "[]\n",
            "secrets.yaml": "",
        }.items():
            try:
                with (config_dir / name).open("x", encoding="utf-8") as file:
                    file.write(contents)
            except FileExistsError:
                pass
        (config_dir / "themes").mkdir(exist_ok=True)
        with config.open("x", encoding="utf-8") as file:
            file.write(DEFAULT_CONFIG + "\n" + INCLUDE + "\n")
        return

    # Inspect YAML nodes without resolving Home Assistant's custom tags.
    with config.open("r", encoding="utf-8", newline="") as file:
        original = file.read()
    root = yaml.compose(original, Loader=yaml.SafeLoader)
    if root is not None:
        if not isinstance(root, yaml.MappingNode) or root.flow_style:
            raise ValueError("configuration.yaml is not a block mapping; refusing to edit it")
        recorder = [value for key, value in root.value
                    if isinstance(key, yaml.ScalarNode) and key.value == "recorder"]
        if recorder:
            if (len(recorder) == 1 and isinstance(recorder[0], yaml.ScalarNode)
                    and recorder[0].tag == "!include" and recorder[0].value == "recorder.yaml"):
                return
            raise ValueError("Existing recorder configuration conflicts with managed include; refusing to overwrite it")
        if any(key.tag == "tag:yaml.org,2002:merge" for key, _ in root.value):
            raise ValueError("configuration.yaml uses a root YAML merge; refusing to edit it")
    newline = "\r\n" if "\r\n" in original else "\n"
    # Insert before an explicit YAML document end, if present.
    end = next((token.start_mark.index for token in yaml.scan(original)
                if isinstance(token, yaml.DocumentEndToken)), len(original))
    before, after = original[:end], original[end:]
    updated = before + (newline if before and not before.endswith(newline) else "") + newline + INCLUDE + newline + after
    # Verify the new include is a valid top-level key before writing.
    parsed = yaml.compose(updated, Loader=yaml.SafeLoader)
    if not isinstance(parsed, yaml.MappingNode) or not any(
        key.value == "recorder" and value.tag == "!include" and value.value == "recorder.yaml"
        for key, value in parsed.value
    ):
        raise ValueError("Unable to add top-level Recorder include")

    # Replace atomically, preserving ownership and permissions.
    target = config.resolve()
    stat = target.stat()
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                     dir=target.parent, delete=False) as file:
        temp = Path(file.name)
        try:
            file.write(updated)
            file.flush()
            os.fsync(file.fileno())
            os.chown(temp, stat.st_uid, stat.st_gid)
            os.chmod(temp, stat.st_mode & 0o7777)
            os.replace(temp, target)
        finally:
            temp.unlink(missing_ok=True)


if __name__ == "__main__":
    ensure_recorder(Path("/config"))
    # Keep the image's normal S6 initialization as PID 1.
    os.execv("/init", ["/init", *sys.argv[1:]])
