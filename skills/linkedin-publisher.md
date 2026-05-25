---
name: linkedin-publisher
description: Publish content to LinkedIn via the Posts API (v202506). Handles text, image, carousel/PDF, and video posts. Manages the content queue.
version: 1.0.0
metadata:
  hermes:
    tags: [linkedin, publishing, api, social-media]
    category: content
    config:
      - key: linkedin.access_token
        description: "LinkedIn OAuth 2.0 access token"
        prompt: "Enter your LinkedIn access token (from LinkedIn Developer Portal)"
      - key: linkedin.person_urn
        description: "Your LinkedIn person URN (e.g., urn:li:person:abc123)"
        prompt: "Enter your LinkedIn person URN"
      - key: linkedin.org_urn
        description: "Organization URN for company page posting (optional)"
        prompt: "Enter your LinkedIn organization URN (leave blank to skip)"
        default: ""
---

# LinkedIn Publisher

## When to Use
When you need to publish content to LinkedIn or manage the content queue. Use after content has been written and visuals generated.

## Setup (One-Time)
1. Go to https://www.linkedin.com/developers/ → Create App
2. Add the **Share on LinkedIn** product (grants `w_member_social`, no review needed)
3. Add **Sign In with LinkedIn using OpenID Connect**
4. Generate an OAuth 2.0 access token via the authorization code flow
5. Get your person URN: `GET https://api.linkedin.com/v2/userinfo` → the `sub` field is your person ID
6. Run `hermes config set linkedin.access_token YOUR_TOKEN`
7. Run `hermes config set linkedin.person_urn urn:li:person:YOUR_ID`
8. For company pages: Apply for **Community Management API** (requires LinkedIn review)

## Procedure

### Publishing a post
Run the publish script:
```bash
# Text-only post
python3 ~/.hermes/scripts/linkedin_publish.py publish \
  --text "Your post text here"

# Image + text post
python3 ~/.hermes/scripts/linkedin_publish.py publish \
  --text "Caption text" \
  --image ~/.hermes/data/linkedin-assets/post-20260524.png

# Carousel (PDF) post
python3 ~/.hermes/scripts/linkedin_publish.py publish \
  --text "Commentary text" \
  --pdf ~/.hermes/data/linkedin-assets/carousel-20260524.pdf \
  --pdf-title "My Carousel Title"

# Post to company page
python3 ~/.hermes/scripts/linkedin_publish.py publish \
  --text "Company update" \
  --profile organization
```

### Managing the content queue
```bash
# Add a post to the queue
python3 ~/.hermes/scripts/linkedin_publish.py queue-add \
  --text "Post text" \
  --publish-date "2026-05-26" \
  --pillar "voice-ai-products" \
  --content-type "text" \
  --status "review"

# List queued posts
python3 ~/.hermes/scripts/linkedin_publish.py queue-list

# Approve a post
python3 ~/.hermes/scripts/linkedin_publish.py queue-approve --id POST_ID

# Publish all approved posts scheduled for today
python3 ~/.hermes/scripts/linkedin_publish.py queue-publish-due

# Reject a post with feedback
python3 ~/.hermes/scripts/linkedin_publish.py queue-reject --id POST_ID --reason "Hook is weak"
```

### Checking engagement (when available)
```bash
python3 ~/.hermes/scripts/linkedin_publish.py metrics --days 7
```

## Environment Variables
These are read from `~/.hermes/.env` or `config.yaml` skill config:
- `LINKEDIN_ACCESS_TOKEN` — OAuth 2.0 bearer token (60-day expiry)
- `LINKEDIN_PERSON_URN` — `urn:li:person:{id}`
- `LINKEDIN_ORG_URN` — `urn:li:organization:{id}` (optional)

## Rate Limits
- 150 posts per day per LinkedIn account
- HTTP 429 on breach — script uses exponential backoff
- Token expires after 60 days — refresh before expiry

## Pitfalls
- LinkedIn API returns 201 with no body on success — check status code, not body
- Media uploads require initialize → PUT binary → reference URN (3-step flow)
- Carousels are PDF documents, not a native carousel type — upload via Documents API
- LinkedIn suppresses reach for posts with external links — put links in first comment instead
- Token refresh: use the refresh_token grant type before the 60-day expiry

## Verification
After publishing, check the LinkedIn feed to confirm the post appears. The script prints the post ID on success.
