#!/usr/bin/env bash
# Test NMDC submission portal auth for both prod and data-dev.
#
# Usage:
#   # Test production
#   ./scripts/test_submission_portal_auth.sh prod YOUR_REFRESH_TOKEN
#
#   # Test data-dev
#   ./scripts/test_submission_portal_auth.sh dev YOUR_REFRESH_TOKEN
#
# How to get a refresh token:
#   1. Log in to the portal in your browser:
#      - Production: https://data.microbiomedata.org/
#      - Data-dev:   https://data-dev.microbiomedata.org/
#   2. Open DevTools (F12) -> Application -> Local Storage
#   3. Find the key "storage.refreshToken" and copy its value
#
# The token is a JWT tied to your ORCID login. Each environment has its own token.
# Tokens expire after 365 days.

set -euo pipefail

ENV="${1:-}"
TOKEN="${2:-}"

if [[ -z "$ENV" || -z "$TOKEN" ]]; then
    echo "Usage: $0 <prod|dev> <refresh_token>"
    exit 1
fi

case "$ENV" in
    prod)
        BASE_URL="https://data.microbiomedata.org"
        ;;
    dev)
        BASE_URL="https://data-dev.microbiomedata.org"
        ;;
    *)
        echo "Error: first argument must be 'prod' or 'dev', got '$ENV'"
        exit 1
        ;;
esac

echo "=== Testing $ENV ($BASE_URL) ==="

# Step 1: Exchange refresh token for access token
echo ""
echo "Step 1: Exchanging refresh token for access token..."
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/refresh" \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$TOKEN\"}")

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    if 'access_token' in r:
        print(r['access_token'])
    else:
        print('FAIL', file=sys.stderr)
        print(json.dumps(r, indent=2), file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f'FAIL: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)

if [[ "$ACCESS_TOKEN" == FAIL* ]]; then
    echo "  FAILED to get access token:"
    echo "  $ACCESS_TOKEN"
    exit 1
fi
echo "  OK - got access token (${#ACCESS_TOKEN} chars)"

# Step 2: Fetch submission count
echo ""
echo "Step 2: Fetching submission count..."
SUB_RESPONSE=$(curl -s "$BASE_URL/api/metadata_submission?limit=1" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$SUB_RESPONSE" | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    count = r.get('count', 'UNKNOWN')
    results = r.get('results', [])
    print(f'  OK - {count} submissions visible')
    if results:
        sub = results[0]
        print(f'  First submission: id={sub.get(\"id\", \"?\")}, status={sub.get(\"status\", \"?\")}')
    if count == 0:
        print('  WARNING: count=0 may mean you need admin privileges on this environment.')
        print('  Ask Patrick Kalita, Shreyas Cholia, or Eric Cavanna to set is_admin=True for your ORCID.')
except Exception as e:
    print(f'  FAIL: {e}')
    sys.exit(1)
"

echo ""
echo "=== $ENV auth test complete ==="
