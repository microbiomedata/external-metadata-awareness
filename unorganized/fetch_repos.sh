#!/bin/bash

# GitHub Repository Metadata Fetcher
# Fetches repo name, first/last commit dates, description, and README for specified owners

set -e

# Configuration
DELAY=0.2  # Delay between API calls in seconds
OUTPUT_DIR="./repo_data"
OWNERS=()
FETCH_CONTRIBUTORS=false  # Whether to fetch contributor stats

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
usage() {
    echo "Usage: $0 -o owner1 [-o owner2 ...] [-d output_dir] [-s delay] [-c]"
    echo "  -o: GitHub owner/organization (can be specified multiple times)"
    echo "  -d: Output directory (default: ./repo_data)"
    echo "  -s: Delay between requests in seconds (default: 0.2)"
    echo "  -c: Fetch contributor statistics (top 10 contributors with commit counts)"
    echo ""
    echo "Example: $0 -o torvalds -o github -d ./data -s 0.3 -c"
    exit 1
}

while getopts "o:d:s:ch" opt; do
    case $opt in
        o) OWNERS+=("$OPTARG");;
        d) OUTPUT_DIR="$OPTARG";;
        s) DELAY="$OPTARG";;
        c) FETCH_CONTRIBUTORS=true;;
        h) usage;;
        *) usage;;
    esac
done

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed${NC}"
    echo "Install it with: brew install jq (macOS) or apt-get install jq (Linux)"
    exit 1
fi

# Check if owners were provided
if [ ${#OWNERS[@]} -eq 0 ]; then
    echo -e "${RED}Error: No owners specified${NC}"
    usage
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}GitHub Repository Metadata Fetcher${NC}"
echo "=================================="
echo "Owners: ${OWNERS[*]}"
echo "Output: $OUTPUT_DIR"
echo "Delay: ${DELAY}s between requests"
echo "Contributors: $([ "$FETCH_CONTRIBUTORS" = true ] && echo "Yes (top 10)" || echo "No")"
echo ""

# Check rate limit
check_rate_limit() {
    local remaining=$(gh api rate_limit | jq '.rate.remaining')
    local limit=$(gh api rate_limit | jq '.rate.limit')
    local reset=$(gh api rate_limit | jq '.rate.reset')
    local reset_time=$(date -r "$reset" 2>/dev/null || date -d "@$reset" 2>/dev/null || echo "unknown")
    
    echo -e "${YELLOW}Rate limit: $remaining/$limit remaining (resets at $reset_time)${NC}"
    
    if [ "$remaining" -lt 100 ]; then
        echo -e "${RED}Warning: Low rate limit remaining!${NC}"
    fi
}

# Counter for periodic rate limit checks
REPO_COUNTER=0
CHECK_INTERVAL=20  # Check rate limit every 20 repos

check_rate_limit

# Process each owner
for owner in "${OWNERS[@]}"; do
    echo -e "\n${GREEN}Processing owner: $owner${NC}"
    
    owner_dir="$OUTPUT_DIR/$owner"
    mkdir -p "$owner_dir"
    
    # Get list of repositories
    echo "Fetching repository list..."
    repos=$(gh repo list "$owner" --limit 1000 --json name --jq '.[].name')
    
    if [ -z "$repos" ]; then
        echo -e "${RED}No repositories found for $owner${NC}"
        continue
    fi
    
    repo_count=$(echo "$repos" | wc -l | tr -d ' ')
    echo "Found $repo_count repositories"
    
    current=0
    # Process each repository
    while IFS= read -r repo; do
        current=$((current + 1))
        REPO_COUNTER=$((REPO_COUNTER + 1))
        
        # Periodic rate limit check
        if [ $((REPO_COUNTER % CHECK_INTERVAL)) -eq 0 ]; then
            echo ""
            check_rate_limit
        fi
        
        echo -e "\n[$current/$repo_count] ${YELLOW}$owner/$repo${NC}"
        
        repo_file="$owner_dir/${repo}.json"
        readme_file="$owner_dir/${repo}_README.md"
        
        # Fetch repository metadata
        echo "  Fetching metadata..."
        gh repo view "$owner/$repo" --json name,description,createdAt,updatedAt,url,defaultBranchRef > "$repo_file" 2>/dev/null || {
            echo -e "  ${RED}Failed to fetch metadata${NC}"
            continue
        }
        
        sleep "$DELAY"
        
        # Fetch first commit date
        echo "  Fetching first commit..."
        first_commit=$(gh api "repos/$owner/$repo/commits?per_page=1&sha=$(jq -r '.defaultBranchRef.name' "$repo_file")" \
            --jq 'if . == null or . == [] then "N/A" else (. | sort_by(.commit.author.date) | first | .commit.author.date) end' 2>/dev/null || echo "N/A")
        
        sleep "$DELAY"
        
        # Fetch last commit date
        echo "  Fetching last commit..."
        last_commit=$(gh api "repos/$owner/$repo/commits?per_page=1" \
            --jq 'if . == null or . == [] then "N/A" else (first | .commit.author.date) end' 2>/dev/null || echo "N/A")
        
        sleep "$DELAY"
        
        # Add commit dates to metadata
        jq --arg first "$first_commit" --arg last "$last_commit" \
            '. + {firstCommitDate: $first, lastCommitDate: $last}' \
            "$repo_file" > "${repo_file}.tmp" && mv "${repo_file}.tmp" "$repo_file"
        
        # Fetch contributors if requested
        if [ "$FETCH_CONTRIBUTORS" = true ]; then
            echo "  Fetching top contributors..."
            contributors=$(gh api "repos/$owner/$repo/contributors?per_page=10" \
                --jq '[.[] | {login: .login, contributions: .contributions}]' 2>/dev/null || echo "[]")
            
            # Add contributors to metadata
            jq --argjson contribs "$contributors" \
                '. + {topContributors: $contribs}' \
                "$repo_file" > "${repo_file}.tmp" && mv "${repo_file}.tmp" "$repo_file"
            
            sleep "$DELAY"
        fi
        
        # Fetch README
        echo "  Fetching README..."
        if gh api "repos/$owner/$repo/readme" --jq '.content' 2>/dev/null | tr -d '\n' | base64 -d > "$readme_file" 2>/dev/null; then
            if [ -s "$readme_file" ]; then
                echo -e "  ${GREEN}README fetched${NC}"
            else
                echo -e "  ${YELLOW}No README found${NC}"
                echo "No README available" > "$readme_file"
            fi
        else
            echo -e "  ${YELLOW}No README found${NC}"
            echo "No README available" > "$readme_file"
        fi
        
        sleep "$DELAY"
        
        echo -e "  ${GREEN}✓ Complete${NC}"
    done <<< "$repos"
    
    # Create summary file
    summary_file="$owner_dir/_SUMMARY.json"
    echo "Creating summary..."
    jq -s '.' "$owner_dir"/*.json 2>/dev/null | grep -v "_SUMMARY" > "$summary_file" || echo "[]" > "$summary_file"
    
    echo -e "${GREEN}Completed $owner: $repo_count repositories processed${NC}"
done

echo -e "\n${GREEN}All done!${NC}"
check_rate_limit
echo -e "\nData saved to: $OUTPUT_DIR"
