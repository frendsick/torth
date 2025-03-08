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
            log "WARNING" "Please install missing dependencies manually:" "$missing_dependencies"
            exit 0
        fi
    fi

    log "SUCCESS" "All set. Happy hacking!" ""
}

are_you_sure() {
    if [ "$#" -ne 1 ]; then
        log "ERROR" "Invalid arguments" "Usage: are_you_sure <message>"
        exit 1
    fi

    message="$1"

    while true; do
        read -p "$message (Y/n) " yn </dev/tty
        case $yn in
        # Interpret empty answer as yes
        "")
            echo true
            break
            ;;
        [Yy])
            echo true
            break
            ;;
        [Nn])
            echo false
            break
            ;;
        *) ;;
        esac
    done
}

download_asset() {
    if [ "$#" -ne 2 ]; then
        log "ERROR" "Invalid arguments" "Usage: download_asset <url> <output_file>"
        exit 1
    fi

    url="$1"
    output_file="$2"
    should_download=true

    if [ -e "$output_file" ]; then
        log "INFO" "File already exists" "$output_file"
        should_download=$(are_you_sure "Reinstall $output_file?")
    fi

    if $should_download; then
        log "SUCCESS" "Download asset" "$output_file"
        if ! curl --silent --location --output "$output_file" "$url"; then
            log "WARNING" "Download failed" "$output_file"
        fi
    else
        log "INFO" "Skip downloading asset" "$output_file"
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
        log "ERROR" "Invalid arguments" "Usage: install_dependencies <dependencies>"
        exit 1
    fi

    dependencies="$1"
    distro=$(
        command -v lsb_release >/dev/null 2>&1 &&
            lsb_release -i | awk '{print $NF}'
    )

    # Debian derivates
    if [ "$distro" = "Debian" ] ||
        [ "$distro" = "Kali" ] ||
        [ "$distro" = "Ubuntu" ]; then
        # APT has `ld` in the `binutils` package
        install_packages "apt" "$(echo "$dependencies" | sed "s/ld/binutils/")"
    # Could not determine the distro
    elif [ -z "$distro" ]; then
        log "WARNING" "Install dependencies" 'Could not determine the Linux distribution with `lsb_release`'
    # Not supported distro
    else
        log "WARNING" "Install dependencies" "Dependency installation is not implemented for $distro"
    fi
}

install_packages() {
    if [ "$#" -ne 2 ]; then
        log "ERROR" "Invalid arguments" "Usage: install_packages <package_manager> <packages>"
        exit 1
    fi

    package_manager="$1"
    packages="$2"

    # Ask from the user if script should install dependencies
    install=$(are_you_sure "Install dependencies from $package_manager?")

    # Install packages with supported package manager
    if [ "$install" != "true" ]; then
        log "INFO" "Skip dependency install" ""
    elif [ "$package_manager" = "apt" ]; then
        sudo apt-get update && sudo apt-get install -y $packages

        # Verify that dependencies were installed
        missing_dependencies=$(get_missing_dependencies)
        if [ -n "$missing_dependencies" ]; then
            log "ERROR" "Dependency installation failed" ""
        fi
    fi
}

log() {
    if [ "$#" -ne 3 ]; then
        log "ERROR" "Invalid arguments" "Usage: log <log_level> <summary> <description>"
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
        log "ERROR" "Unknown log level" "$log_level"
        exit 1
    fi

    if [ "$log_level" = "ERROR" ] || [ "$log_level" = "WARNING" ]; then
        # Print log to stderr
        >&2 printf "%b %-*s %s\n" "$prefix" "$SUMMARY_WIDTH" "$summary" "$description"
    else
        # Print log to stdout
        printf "%b %-*s %s\n" "$prefix" "$SUMMARY_WIDTH" "$summary" "$description"
    fi
}

main
