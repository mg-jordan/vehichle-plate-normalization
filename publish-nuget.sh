#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$ROOT_DIR/src/SaudiPlate/SaudiPlate.csproj"
OUTPUT_DIR="$ROOT_DIR/artifacts"

if [[ -z "${NUGET_API_KEY:-}" ]]; then
  echo "Set NUGET_API_KEY before running this script."
  exit 1
fi

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

dotnet restore "$ROOT_DIR/SaudiPlateNet.sln"
dotnet test "$ROOT_DIR/SaudiPlateNet.sln" -c Release --no-restore
dotnet pack "$PROJECT" -c Release --no-restore -o "$OUTPUT_DIR"
dotnet nuget push "$OUTPUT_DIR"/*.nupkg --api-key "$NUGET_API_KEY" --source https://api.nuget.org/v3/index.json
