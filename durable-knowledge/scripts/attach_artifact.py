#!/usr/bin/env python3
"""Attach an immutable content-addressed evidence snapshot to a vault."""

import argparse
import errno
import hashlib
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

_ARTIFACT_ROOT = Path("Knowledge/Artifacts")
_MARKER = Path("_durable-knowledge/ROOT.md")
_SAFE_SUFFIX = re.compile(r"^\.[a-z0-9][a-z0-9+_-]*$")
_CHUNK_SIZE = 1024 * 1024


class _ArtifactError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(_CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def _ensure_managed_path(vault: Path, relative: Path) -> Path:
    current = vault
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise _ArtifactError("managed artifact path must not contain symlinks")

    current.mkdir(parents=True, exist_ok=True)
    if current.is_symlink() or not current.is_dir():
        raise _ArtifactError("Knowledge/Artifacts is not a regular directory")
    try:
        current.resolve().relative_to(vault)
    except ValueError as error:
        raise _ArtifactError("managed artifact path escapes the vault") from error
    return current


def _validate_existing_artifact(directory: Path, digest: str) -> Path:
    if directory.is_symlink() or not directory.is_dir():
        raise _ArtifactError(
            "existing artifact path is not a regular non-symlink directory"
        )
    payloads = sorted(directory.glob("payload.*"))
    if len(payloads) != 1:
        raise _ArtifactError("existing artifact must contain exactly one payload file")
    payload = payloads[0]
    if payload.is_symlink() or not payload.is_file():
        raise _ArtifactError(
            "existing artifact payload is not a regular non-symlink file"
        )
    if _sha256(payload) != digest:
        raise _ArtifactError("existing artifact does not match its content hash")
    return payload


def _attach(vault: Path, source: Path) -> tuple[Path, str, bool]:
    marker = vault / _MARKER
    if not marker.is_file() or marker.is_symlink():
        raise _ArtifactError(
            "vault marker _durable-knowledge/ROOT.md is missing or not a regular file"
        )
    if source.is_symlink():
        raise _ArtifactError("source file must not be a symlink")
    if not source.is_file():
        raise _ArtifactError("source file is missing or not a regular file")

    suffix = source.suffix.lower()
    if not suffix:
        raise _ArtifactError("source file must have an extension")
    if _SAFE_SUFFIX.fullmatch(suffix) is None:
        raise _ArtifactError(
            "source file extension is not safe for an artifact filename"
        )

    artifact_root = _ensure_managed_path(vault, _ARTIFACT_ROOT)
    temporary_directory = Path(tempfile.mkdtemp(prefix=".artifact-", dir=artifact_root))
    temporary_payload = temporary_directory / f"payload{suffix}"
    try:
        hasher = hashlib.sha256()
        with (
            source.open("rb") as source_stream,
            temporary_payload.open("xb") as destination,
        ):
            while chunk := source_stream.read(_CHUNK_SIZE):
                destination.write(chunk)
                hasher.update(chunk)
            destination.flush()
            os.fsync(destination.fileno())

        digest = hasher.hexdigest()
        target_directory = artifact_root / f"artifact-sha256-{digest}"
        if target_directory.exists() or target_directory.is_symlink():
            payload = _validate_existing_artifact(target_directory, digest)
            return payload, digest, False

        try:
            os.rename(temporary_directory, target_directory)
            temporary_directory = target_directory
            created = True
        except OSError as error:
            if error.errno not in {errno.EEXIST, errno.ENOTEMPTY}:
                raise
            payload = _validate_existing_artifact(target_directory, digest)
            return payload, digest, False

        return target_directory / temporary_payload.name, digest, created
    finally:
        if temporary_directory.exists() and temporary_directory.name.startswith(
            ".artifact-"
        ):
            shutil.rmtree(temporary_directory)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, required=True, help="Target vault")
    parser.add_argument(
        "--file", type=Path, required=True, help="Evidence file to snapshot"
    )
    return parser


def _main() -> int:
    args = _build_parser().parse_args()
    vault = args.vault.expanduser().resolve()
    source = args.file.expanduser()
    try:
        artifact, digest, created = _attach(vault, source)
    except (_ArtifactError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Artifact: {artifact.relative_to(vault)}")
    print(f"SHA-256: {digest}")
    print(f"Source reference: vault:artifact:sha256:{digest}")
    print(f"Created: {'yes' if created else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
