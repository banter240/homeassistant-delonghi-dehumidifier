#!/bin/bash
#
# Release asset preparation for semantic-release (HACS zip + manifest version).
# Usage: ./scripts/publish.sh <version>
#

set -e

COLOR_BLUE='\033[1;34m'
COLOR_GREEN='\033[1;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[1;31m'
COLOR_RESET='\033[0m'
log_info() { echo -e "${COLOR_BLUE}INFO: $1${COLOR_RESET}"; }
log_success() { echo -e "${COLOR_GREEN}SUCCESS: $1${COLOR_RESET}"; }
log_warn() { echo -e "${COLOR_YELLOW}WARNING: $1${COLOR_RESET}"; }
log_error() { echo -e "${COLOR_RED}ERROR: $1${COLOR_RESET}" >&2; }

log_info "Running pre-flight checks..."
for tool in zip jq; do
  if ! command -v "$tool" &> /dev/null; then
    log_error "Required tool '$tool' is not installed."
    exit 1
  fi
done
if [ $# -ne 1 ]; then
  log_error "A version number must be provided. Usage: $0 <version>"
  exit 1
fi

readonly NEXT_RELEASE_VERSION="$1"
readonly DOMAIN="delonghi_dehumidifier_api"
readonly DIST_DIR="dist"
readonly ZIP_FILENAME="${DOMAIN}_${NEXT_RELEASE_VERSION}.zip"
readonly SOURCE_DIR="custom_components/${DOMAIN}"
readonly COMPONENT_MANIFEST_PATH="${SOURCE_DIR}/manifest.json"

log_info "Starting release asset preparation for version ${NEXT_RELEASE_VERSION}..."

if [ -f "$COMPONENT_MANIFEST_PATH" ]; then
  log_info "Updating version in '${COMPONENT_MANIFEST_PATH}'..."
  jq ".version = \"${NEXT_RELEASE_VERSION}\"" "$COMPONENT_MANIFEST_PATH" \
    > "${COMPONENT_MANIFEST_PATH}.tmp" \
    && mv "${COMPONENT_MANIFEST_PATH}.tmp" "$COMPONENT_MANIFEST_PATH"
  log_success "'${COMPONENT_MANIFEST_PATH}' updated to version ${NEXT_RELEASE_VERSION}."
else
  log_warn "'${COMPONENT_MANIFEST_PATH}' not found. Cannot update version."
fi

log_info "Ensuring distribution directory '${DIST_DIR}' exists..."
mkdir -p "${DIST_DIR}"

log_info "Creating ZIP archive at '${DIST_DIR}/${ZIP_FILENAME}'..."
cd "${SOURCE_DIR}"
zip -r "../../${DIST_DIR}/${ZIP_FILENAME}" . -x "*/__pycache__/*" "*.pyc" ".DS_Store"
cd ../..
log_success "ZIP archive with correct HACS structure created successfully."

log_info "Running 'git status'..."
git status

echo
log_success "Release asset preparation complete for version ${NEXT_RELEASE_VERSION}."
