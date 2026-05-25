#!/bin/bash
# LinkedIn Content Swarm — Hermes Installer
# Usage: git clone <repo> /tmp/linkedin-swarm && cd /tmp/linkedin-swarm && bash install.sh
set -e

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
echo "Installing LinkedIn Content Swarm to ${HERMES_HOME}..."

# Create directories
mkdir -p "$HERMES_HOME/skills" "$HERMES_HOME/scripts" "$HERMES_HOME/data/linkedin-assets" "$HERMES_HOME/profiles/architect"

# Install skills (won't overwrite existing)
for skill in skills/*.md; do
  name=$(basename "$skill")
  dst="$HERMES_HOME/skills/$name"
  if [ ! -f "$dst" ]; then
    cp "$skill" "$dst"
    echo "  Installed skill: $name"
  else
    echo "  Skipped (exists): $name"
  fi
done

# Install scripts
for script in scripts/*.py; do
  name=$(basename "$script")
  dst="$HERMES_HOME/scripts/$name"
  cp "$script" "$dst"
  chmod +x "$dst"
  echo "  Installed script: $name"
done

# Install Architect profile
if [ -f "profiles/architect/SOUL.md" ]; then
  cp "profiles/architect/SOUL.md" "$HERMES_HOME/profiles/architect/SOUL.md"
  echo "  Installed Architect profile"
fi

# Add LinkedIn URN if not present
if ! grep -q "LINKEDIN_PERSON_URN" "$HERMES_HOME/.env" 2>/dev/null; then
  echo 'LINKEDIN_PERSON_URN=urn:li:person:B4AUAahLRC' >> "$HERMES_HOME/.env"
  echo "  Added LINKEDIN_PERSON_URN to .env"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Installed:"
ls "$HERMES_HOME/skills/" | grep -E "content|linkedin|visual" | sed 's/^/  skill: /'
ls "$HERMES_HOME/scripts/" | grep linkedin | sed 's/^/  script: /'
echo ""
echo "Next steps:"
echo "  1. Add your LinkedIn token: hermes config set LINKEDIN_ACCESS_TOKEN <token>"
echo "  2. Create cron jobs (in Hermes chat):"
echo '     /cron create "Daily LinkedIn Content" --schedule "0 6 * * 1-5" --skills content-strategy,content-writer,visual-producer,linkedin-publisher --deliver telegram'
echo '     /cron create "Weekly LinkedIn Digest" --schedule "0 9 * * 1" --skills content-strategy,linkedin-publisher --deliver telegram'
echo "  3. Test: /content-strategy then ask for a post"
