#!/bin/sh

# Exit if any command exists with a non-zero status
set -e

# Configuration
GITHUB_REPO="frendsick/torth"
RELEASE_VERSION="latest"
TORTH_COMPILER="torth"
TORTH_STD_LIBRARY="std.torth"

# List of dependencies
DEPENDENCIES="ld nasm"

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

    # Offer to install missing dependencies for supported distros
    missing_dependencies=$(get_missing_dependencies)
    if [ -n "$missing_dependencies" ]; then
        log "WARNING" "Dependencies missing" "$missing_dependencies"
        install_dependencies "$missing_dependencies"

        # Verify that dependencies were installed
        missing_dependencies=$(get_missing_dependencies)
        if [ -n "$missing_dependencies" ]; then
            log "ERROR" "Dependency install failed" "$missing_dependencies"
            exit 1
        fi
    fi

    log "SUCCESS" "All set. Happy hacking!" ""
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

get_missing_dependencies() {
    # Gather missing packages to this variable
    missing_dependencies=""

    for dependency in $DEPENDENCIES; do
        # Check if dependency already exists
        if ! command -v "$dependency" >/dev/null 2>&1; then
            missing_dependencies="$dependency $missing_dependencies"
        fi
    done

    echo "$missing_dependencies"
}

# Install dependencies for supported Linux distros
install_dependencies() {
    if [ "$#" -ne 1 ]; then
        >&2 log "ERROR" "Invalid arguments" "Usage: install_dependencies <dependencies>"
        exit 1
    fi

    dependencies="$1"
    distributor_id=$(
        command -v lsb_release >/dev/null 2>&1 &&
            lsb_release -i | awk '{print $NF}'
    )

    # Debian derivates
    if [ "$distributor_id" = "Debian" ] ||
        [ "$distributor_id" = "Kali" ] ||
        [ "$distributor_id" = "Ubuntu" ]; then
        # APT has `ld` in the `binutils` package
        install_packages "apt" "$(echo "$dependencies" | sed "s/ld/binutils/")"
    fi
}

install_packages() {
    if [ "$#" -ne 2 ]; then
        >&2 log "ERROR" "Invalid arguments" "Usage: install_packages <package_manager> <packages>"
        exit 1
    fi

    package_manager="$1"
    packages="$2"

    # Ask from the user if script should install dependencies
    while true; do
        read -p "Install dependencies from $package_manager? (Y/n) " yn
        case $yn in
        "") break ;; # Interpret empty answer as yes
        [Yy]) break ;;
        [Nn]) return 1 ;;
        esac
    done

    # Install packages with supported package manager
    if [ "$package_manager" = "apt" ]; then
        sudo apt-get update && sudo apt-get install -y $packages
    fi
}

log() {
    if [ "$#" -ne 3 ]; then
        >&2 log "ERROR" "Invalid arguments" "Usage: log <log_level> <summary> <description>"
        exit 1
    fi

    # $description starts at least $SUMMARY_WIDTH characters from the beginning of $summary
    SUMMARY_WIDTH=26
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
