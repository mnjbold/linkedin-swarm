#!/usr/bin/env python3
"""
LinkedIn Publisher + Content Queue Manager for Hermes-Agent.

Commands:
  publish       — Post content to LinkedIn (text, image, carousel/PDF)
  queue-add     — Add a post to the content queue
  queue-list    — List queued posts
  queue-approve — Approve a queued post
  queue-reject  — Reject a queued post with feedback
  queue-publish-due — Publish all approved posts scheduled for today
  metrics       — Fetch engagement metrics (placeholder)

Environment:
  LINKEDIN_ACCESS_TOKEN  — OAuth 2.0 bearer token
  LINKEDIN_PERSON_URN    — urn:li:person:{id}
  LINKEDIN_ORG_URN       — urn:li:organization:{id} (optional)

Queue storage: ~/.hermes/data/linkedin-queue.json
"""

import argparse
import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from datetime import datetime, date
from pathlib import Path

API_BASE = "https://api.linkedin.com/rest"
API_VERSION = "202506"
QUEUE_PATH = Path.home() / ".hermes" / "data" / "linkedin-queue.json"
ASSETS_DIR = Path.home() / ".hermes" / "data" / "linkedin-assets"


# ─── LinkedIn API helpers ───────────────────────────────────────

def get_token():
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not token:
        # Try reading from .env file
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not token:
        print("ERROR: LINKEDIN_ACCESS_TOKEN not found in env or ~/.hermes/.env", file=sys.stderr)
        sys.exit(1)
    return token


def get_person_urn():
    urn = os.environ.get("LINKEDIN_PERSON_URN")
    if not urn:
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("LINKEDIN_PERSON_URN="):
                    urn = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not urn:
        print("ERROR: LINKEDIN_PERSON_URN not found", file=sys.stderr)
        sys.exit(1)
    return urn


def get_org_urn():
    urn = os.environ.get("LINKEDIN_ORG_URN", "")
    if not urn:
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("LINKEDIN_ORG_URN="):
                    urn = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return urn or None


def api_headers(content_type="application/json"):
    h = {
        "Authorization": f"Bearer {get_token()}",
        "LinkedIn-Version": API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if content_type:
        h["Content-Type"] = content_type
    return h


def get_author_urn(profile="personal"):
    if profile == "organization":
        urn = get_org_urn()
        if not urn:
            print("ERROR: LINKEDIN_ORG_URN required for organization profile", file=sys.stderr)
            sys.exit(1)
        return urn
    return get_person_urn()


def upload_media(file_path, media_type, author_urn):
    """Upload image or document to LinkedIn. Returns the media URN."""
    endpoint = "images" if media_type == "image" else "documents"

    # Initialize upload
    payload = {"initializeUploadRequest": {"owner": author_urn}}
    req = urllib.request.Request(
        f"{API_BASE}/{endpoint}?action=initializeUpload",
        data=json.dumps(payload).encode(),
        headers=api_headers(),
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    upload_url = data["value"]["uploadUrl"]
    media_urn = data["value"][media_type if media_type == "image" else "document"]

    # Upload binary
    with open(file_path, "rb") as f:
        binary = f.read()

    ct = "application/octet-stream" if media_type == "image" else "application/pdf"
    upload_req = urllib.request.Request(
        upload_url,
        data=binary,
        headers={"Authorization": f"Bearer {get_token()}", "Content-Type": ct},
        method="PUT"
    )
    urllib.request.urlopen(upload_req)
    print(f"  {media_type} uploaded: {media_urn}")
    return media_urn


def publish_to_linkedin(text, image_path=None, pdf_path=None, pdf_title="", profile="personal"):
    """Publish a post to LinkedIn."""
    author = get_author_urn(profile)

    payload = {
        "author": author,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    if pdf_path:
        doc_urn = upload_media(pdf_path, "document", author)
        payload["content"] = {"media": {"id": doc_urn, "title": pdf_title or "Carousel"}}
    elif image_path:
        img_urn = upload_media(image_path, "image", author)
        payload["content"] = {"media": {"id": img_urn}}

    req = urllib.request.Request(
        f"{API_BASE}/posts",
        data=json.dumps(payload).encode(),
        headers=api_headers(),
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            post_id = resp.headers.get("x-restli-id", "unknown")
            print(f"SUCCESS: Published to LinkedIn. Post ID: {post_id}")
            return {"success": True, "post_id": post_id}
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"ERROR: HTTP {e.code} — {body}", file=sys.stderr)
        return {"success": False, "error": e.code, "body": body}


# ─── Content Queue ──────────────────────────────────────────────

def load_queue():
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if QUEUE_PATH.exists():
        return json.loads(QUEUE_PATH.read_text())
    return {"posts": [], "updated_at": datetime.utcnow().isoformat()}


def save_queue(queue):
    queue["updated_at"] = datetime.utcnow().isoformat()
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(queue, indent=2, default=str))


def queue_add(args):
    queue = load_queue()
    post = {
        "id": str(uuid.uuid4())[:8],
        "created_at": datetime.utcnow().isoformat(),
        "publish_date": args.publish_date or date.today().isoformat(),
        "profile": args.profile or "personal",
        "content_type": args.content_type or "text",
        "pillar": args.pillar or "",
        "text": args.text,
        "hashtags": args.hashtags or "",
        "image_path": args.image or "",
        "pdf_path": args.pdf or "",
        "pdf_title": args.pdf_title or "",
        "visual_brief": args.visual_brief or "",
        "status": args.status or "draft",
        "engagement": {},
        "editor_notes": "",
        "linkedin_post_id": ""
    }
    queue["posts"].append(post)
    save_queue(queue)
    print(f"Added to queue: {post['id']} — {post['status']} — scheduled {post['publish_date']}")
    print(f"  Text preview: {post['text'][:100]}...")


def queue_list(args):
    queue = load_queue()
    status_filter = getattr(args, 'status', None)
    posts = queue["posts"]
    if status_filter:
        posts = [p for p in posts if p["status"] == status_filter]

    if not posts:
        print("Queue is empty." if not status_filter else f"No posts with status '{status_filter}'.")
        return

    print(f"{'ID':<10} {'Date':<12} {'Status':<10} {'Type':<10} {'Pillar':<25} {'Preview'}")
    print("-" * 100)
    for p in posts:
        preview = p["text"][:40] + "..." if len(p["text"]) > 40 else p["text"]
        print(f"{p['id']:<10} {p['publish_date']:<12} {p['status']:<10} {p['content_type']:<10} {p.get('pillar',''):<25} {preview}")


def queue_approve(args):
    queue = load_queue()
    for p in queue["posts"]:
        if p["id"] == args.id:
            p["status"] = "approved"
            save_queue(queue)
            print(f"Approved: {args.id}")
            return
    print(f"Post {args.id} not found", file=sys.stderr)


def queue_reject(args):
    queue = load_queue()
    for p in queue["posts"]:
        if p["id"] == args.id:
            p["status"] = "rejected"
            p["editor_notes"] = args.reason or ""
            save_queue(queue)
            print(f"Rejected: {args.id} — {args.reason}")
            return
    print(f"Post {args.id} not found", file=sys.stderr)


def queue_publish_due(args):
    queue = load_queue()
    today = date.today().isoformat()
    due = [p for p in queue["posts"] if p["status"] == "approved" and p["publish_date"] <= today]

    if not due:
        print("No approved posts due for today.")
        return

    for p in due:
        print(f"\nPublishing: {p['id']} ({p['content_type']})...")
        result = publish_to_linkedin(
            text=p["text"],
            image_path=p.get("image_path") or None,
            pdf_path=p.get("pdf_path") or None,
            pdf_title=p.get("pdf_title", ""),
            profile=p.get("profile", "personal")
        )
        if result.get("success"):
            p["status"] = "published"
            p["linkedin_post_id"] = result.get("post_id", "")
            p["published_at"] = datetime.utcnow().isoformat()
        else:
            p["status"] = "failed"
            p["editor_notes"] = f"Publish failed: {result}"

    save_queue(queue)
    published = sum(1 for p in due if p["status"] == "published")
    print(f"\nDone: {published}/{len(due)} posts published.")


def metrics(args):
    """Placeholder for engagement metrics — LinkedIn API access needed."""
    queue = load_queue()
    published = [p for p in queue["posts"] if p["status"] == "published"]
    print(f"Published posts: {len(published)}")
    for p in published:
        print(f"  {p['id']} — {p['publish_date']} — {p['content_type']} — LinkedIn ID: {p.get('linkedin_post_id', 'n/a')}")
    print("\nNote: Full engagement metrics require LinkedIn Marketing API access (separate approval).")


# ─── CLI ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Publisher + Content Queue")
    sub = parser.add_subparsers(dest="command")

    # publish
    pub = sub.add_parser("publish", help="Publish directly to LinkedIn")
    pub.add_argument("--text", required=True)
    pub.add_argument("--image")
    pub.add_argument("--pdf")
    pub.add_argument("--pdf-title", default="")
    pub.add_argument("--profile", default="personal", choices=["personal", "organization"])

    # queue-add
    qa = sub.add_parser("queue-add", help="Add post to content queue")
    qa.add_argument("--text", required=True)
    qa.add_argument("--publish-date")
    qa.add_argument("--profile", default="personal")
    qa.add_argument("--content-type", default="text")
    qa.add_argument("--pillar", default="")
    qa.add_argument("--hashtags", default="")
    qa.add_argument("--image")
    qa.add_argument("--pdf")
    qa.add_argument("--pdf-title", default="")
    qa.add_argument("--visual-brief", default="")
    qa.add_argument("--status", default="draft", choices=["draft", "review", "approved"])

    # queue-list
    ql = sub.add_parser("queue-list", help="List queued posts")
    ql.add_argument("--status", choices=["draft", "review", "approved", "published", "rejected", "failed"])

    # queue-approve
    qap = sub.add_parser("queue-approve", help="Approve a queued post")
    qap.add_argument("--id", required=True)

    # queue-reject
    qr = sub.add_parser("queue-reject", help="Reject a queued post")
    qr.add_argument("--id", required=True)
    qr.add_argument("--reason", default="")

    # queue-publish-due
    sub.add_parser("queue-publish-due", help="Publish all approved posts due today")

    # metrics
    m = sub.add_parser("metrics", help="Show engagement metrics")
    m.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    if args.command == "publish":
        publish_to_linkedin(args.text, args.image, args.pdf, args.pdf_title, args.profile)
    elif args.command == "queue-add":
        queue_add(args)
    elif args.command == "queue-list":
        queue_list(args)
    elif args.command == "queue-approve":
        queue_approve(args)
    elif args.command == "queue-reject":
        queue_reject(args)
    elif args.command == "queue-publish-due":
        queue_publish_due(args)
    elif args.command == "metrics":
        metrics(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
