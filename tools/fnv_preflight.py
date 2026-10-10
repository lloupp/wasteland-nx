#!/usr/bin/env python3
"""Read-only audit of an Epic Games Fallout: New Vegas installation."""
import argparse
import json
import os
from pathlib import Path
import struct
import sys

DLCS = ("DeadMoney.esm", "HonestHearts.esm", "OldWorldBlues.esm",
        "LonesomeRoad.esm", "GunRunnersArsenal.esm")
REQUIRED = ("FalloutNV.esm", "Fallout - Meshes.bsa")


def epic_install_roots(manifests=None):
    """Find install locations from Epic Launcher manifests, without opening games."""
    if manifests is None:
        base = os.environ.get("PROGRAMDATA") or (
            str(Path(os.environ.get("SystemDrive", "C:")) / "ProgramData")
            if sys.platform == "win32" else "")
        if not base:
            return
        manifests = Path(base) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"
    manifests = Path(manifests)
    if not manifests.is_dir():
        return
    for item in sorted(manifests.glob("*.item"))[:2000]:
        try:
            if item.stat().st_size > 2 * 1024 * 1024:
                continue
            meta = json.loads(item.read_text(encoding="utf-8-sig"))
            location = meta.get("InstallLocation")
            label = (str(meta.get("DisplayName", "")) + " " + str(location)).lower()
            if isinstance(location, str) and (
                "falloutnewvegas" in label.replace(" ", "") or
                "falloutnv" in label.replace(" ", "")
            ):
                yield Path(location)
        except (OSError, ValueError, TypeError):
            continue


def find_data(root):
    """Accept Data, game root or Epic's per-language subdirectory."""
    root = Path(root).expanduser()
    if root.is_file() and root.name.lower() == "falloutnv.esm":
        return root.parent
    if not root.is_dir():
        return None
    queue = [root]
    for _ in range(2):
        next_queue = []
        for folder in queue:
            try:
                subs = [p for p in folder.iterdir() if p.is_dir()]
            except OSError:
                continue
            for candidate in [folder] + [p for p in subs if p.name.lower() == "data"]:
                try:
                    if any(p.name.lower() == "falloutnv.esm" and p.is_file()
                           for p in candidate.iterdir()):
                        return candidate
                except OSError:
                    continue
            next_queue.extend(p for p in subs if p.name.lower() != "data" and
                              ("fallout" in p.name.lower() or folder == root))
        queue = next_queue[:100]
    return None


def locate(explicit=None, manifests=None):
    if explicit:
        found = find_data(explicit)
        if found:
            return found, "manual"
        raise ValueError("FalloutNV.esm não encontrado no caminho informado")
    for candidate in epic_install_roots(manifests):
        found = find_data(candidate)
        if found:
            return found, "epic-manifest"
    roots = []
    for key in ("PROGRAMFILES", "PROGRAMFILES(X86)", "EPIC_GAMES"):
        value = os.environ.get(key)
        if value:
            base = Path(value) if key == "EPIC_GAMES" else Path(value) / "Epic Games"
            roots.extend(base / game for game in ("FalloutNewVegas", "Fallout New Vegas"))
    for candidate in roots:
        found = find_data(candidate)
        if found:
            return found, "epic-default"
    raise ValueError("Epic não localizada. Use --data para informar a pasta do jogo")


def probe(file):
    size = file.stat().st_size
    with file.open("rb") as f:
        header = f.read(36)
    ext = file.suffix.lower()
    if ext in (".esm", ".esp"):
        valid = size >= 24 and header.startswith(b"TES4")
    elif ext == ".bsa":
        valid = (size >= 36 and header.startswith(b"BSA\x00") and
                 struct.unpack_from("<I", header, 4)[0] == 104)
    else:
        valid = False
    return {"name": file.name, "bytes": size, "valid_header": valid}


def audit(data, discovery="manual"):
    entries = []
    for file in sorted(Path(data).iterdir(), key=lambda p: p.name.casefold()):
        if file.is_file() and file.suffix.lower() in (".esm", ".esp", ".bsa"):
            try:
                entries.append(probe(file))
            except OSError:
                entries.append({"name": file.name, "valid_header": False})
    indexed = {entry["name"].casefold(): entry for entry in entries}
    missing = [name for name in REQUIRED if name.casefold() not in indexed]
    invalid = [name for name in REQUIRED if name.casefold() in indexed and
               not indexed[name.casefold()]["valid_header"]]
    lang = next((x for x in ("English", "Spanish", "French", "German", "Italian")
                 if Path(data).parent.name.casefold().endswith(" " + x.lower())),
                "not-determined")
    return {
        "project": "Wasteland NX / Fallout: New Vegas",
        "stage": "PC file inspection only",
        "discovery": discovery,
        "language": lang,
        "required_ok": not (missing or invalid),
        "missing_required": missing,
        "invalid_required": invalid,
        "official_dlcs_detected": [x for x in DLCS if x.lower() in indexed],
        "files": entries,
        "notice": "No compatibility or gameplay claim; proprietary data not included."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Wasteland NX Epic preflight (read-only)")
    parser.add_argument("--epic", action="store_true", help="Search the Epic Games installation")
    parser.add_argument("--data", help="Game root or Data directory")
    parser.add_argument("--report", default="newvegas-relatorio.json")
    args = parser.parse_args(argv)
    try:
        data, origin = locate(args.data)
        report = audit(data, origin)
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) +
                                     "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    print("Origem:", report["discovery"], "| idioma:", report["language"])
    print("Arquivos:", len(report["files"]), "| DLCs:", len(report["official_dlcs_detected"]))
    print("Relatório gerado:", args.report)
    if not report["required_ok"]:
        print("Arquivos necessários ausentes ou inválidos.", file=sys.stderr)
        return 1
    print("Pré-verificação concluída (não é teste de port).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
