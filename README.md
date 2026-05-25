# LinkedIn Content Swarm for Hermes-Agent

Autonomous LinkedIn content creation and publishing system built as Hermes-Agent skills.

## Quick Install

```bash
git clone https://github.com/YOUR_USERNAME/linkedin-swarm.git /tmp/linkedin-swarm
cd /tmp/linkedin-swarm
bash install.sh
```

## What's Included

| File | Purpose |
|------|---------|
| `skills/content-strategy.md` | Voice profile, content pillars, algorithm rules, post structures |
| `skills/content-writer.md` | Post generation procedure |
| `skills/linkedin-publisher.md` | LinkedIn API publishing + queue management |
| `skills/visual-producer.md` | Image, carousel, video asset generation |
| `scripts/linkedin_publish.py` | CLI tool for LinkedIn API + content queue |
| `profiles/architect/SOUL.md` | Ops agent persona for diagnostics |
| `install.sh` | One-command installer |

## Setup

1. Clone and install (above)
2. Add LinkedIn credentials: `hermes config set LINKEDIN_ACCESS_TOKEN your_token`
3. Create cron jobs:
   ```
   /cron create "Daily LinkedIn Content" --schedule "0 6 * * 1-5" --skills content-strategy,content-writer,visual-producer,linkedin-publisher --deliver telegram
   /cron create "Weekly LinkedIn Digest" --schedule "0 9 * * 1" --skills content-strategy,linkedin-publisher --deliver telegram
   ```
4. Test: `/content-strategy` then ask for a post

## Content Pillars

1. Building voice AI products (Retell → revenue)
2. Niche-market AI deployment (dental, medical clinics)
3. Geo-arbitrage (Malaysia → US/UAE)
4. Agent infrastructure & ops
5. Bootstrapped founder mindset
6. Voice AI persona design
7. Industry trends & commentary

## Weekly Cadence

- Mon: Thought leadership
- Tue: Technical deep-dive
- Wed: Carousel/visual
- Thu: Story/case study
- Fri: Quick tip

## License

MIT
