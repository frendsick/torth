#!/bin/sh

# Exit if any command exists with a non-zero status
set -e

# Configuration
GITHUB_REPO="frendsick/torth"
RELEASE_VERSION="latest"
TORTH_COMPILER="torth"
TORTH_STD_LIBRARY="std.torth"

# Script entry point
main() {
    # Fetch latest release from the Github REST API
    # https://docs.github.com/en/rest/releases/releases
    log "INFO" "List assets from Github" "$GITHUB_REPO"
    release_json=$(
        curl \
            --silent \
            --header "X-GitHub-Api-Version: 2022-11-28" \
            "https://api.github.com/repos/$GITHUB_REPO/releases/$RELEASE_VERSION"
    )

    # Parse asset name and URL pairs
    release_asset_urls=$(
        echo "$release_json" |
            grep -E '"name"|"browser_download_url"' |
            sed -E 's/[",]//g' |
            awk '
                /name:/ {name=$2}
                /browser_download_url:/ {print name, $2}
            '
    )

    # Handle each asset from the release
    echo "$release_asset_urls" | while read -r asset_name asset_url; do

        # Download the executable and make it executable
        if [ "$asset_name" = "$TORTH_COMPILER" ]; then
            download_asset "$asset_url" "$asset_name"
            chmod +x "$asset_name"
            log "SUCCESS" "Make executable" "$asset_name"

        # Download the standard library
        elif [ "$asset_name" = "$TORTH_STD_LIBRARY" ]; then
            download_asset "$asset_url" "$asset_name"

        else
            log "INFO" "Skipping asset" "$asset_name"
        fi
    done
}

download_asset() {
    if [ "$#" -ne 2 ]; then
        >&2 log "ERROR" "Invalid arguments" "Usage: download_asset <url> <output_file>"
        exit 1
    fi

    url="$1"
    output_file="$2"

    log "SUCCESS" "Download asset" "$output_file"
    if ! curl --silent --location --output "$output_file" "$url"; then
        >&2 log "WARNING" "Download failed" "$output_file"
    fi
}

log() {
    if [ "$#" -ne 3 ]; then
        >&2 log "ERROR" "Invalid arguments" "Usage: log <log_level> <summary> <description>"
        exit 1
    fi

    # $description starts at least $SUMMARY_WIDTH characters from the beginning of $summary
    SUMMARY_WIDTH=24
    log_level="$1"
    summary="$2"
    description="$3"

    # Colors
    ERROR="\e[91m"
    INFO="\e[94m"
    SUCCESS="\e[92m"
    WARNING="\e[1;31m"
    RESET="\e[0m"

    # Construct $prefix based on the log level
    if [ "$log_level" = "INFO" ]; then
        prefix="[${INFO}*${RESET}]" # [*]
    elif [ "$log_level" = "ERROR" ]; then
        prefix="[${ERROR}x${RESET}]" # [x]
    elif [ "$log_level" = "SUCCESS" ]; then
        prefix="[${SUCCESS}+${RESET}]" # [+]
    elif [ "$log_level" = "WARNING" ]; then
        prefix="[${WARNING}-${RESET}]" # [-]
    else
        >&2 log "ERROR" "Unknown log level" "$log_level"
        exit 1
    fi

    # Print log to stdout
    printf "%b %-*s %s\n" "$prefix" "$SUMMARY_WIDTH" "$summary" "$description"
}

main
