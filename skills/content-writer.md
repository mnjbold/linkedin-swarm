---
name: content-writer
description: Writes LinkedIn posts tuned to Muhammad Nurunnabi's voice. Produces text posts, carousel outlines, and video scripts based on content briefs.
version: 1.0.0
metadata:
  hermes:
    tags: [linkedin, writing, content, voice]
    category: content
---

# LinkedIn Content Writer

## When to Use
When generating a LinkedIn post from a content brief. This skill handles the actual writing — the content-strategy skill provides the rules and voice profile.

## Procedure

1. **Load the content-strategy skill first** — it has the voice profile, banned words, post structures, and algorithm rules.

2. **Parse the brief.** Every content brief should include:
   - Topic and pillar (1-7)
   - Angle / hook direction
   - Target format (text / image+text / carousel / video)
   - Any reference material or data points

3. **Select the right post structure** based on format:
   - Text posts → Hook-Story-Lesson, List Post, or Contrarian Take
   - Image posts → Behind-the-Scenes or Micro-Tutorial (pair with generated image)
   - Carousels → List Post structure expanded to slides (1 insight per slide)
   - Video → Script the first 15 seconds as a hook, then deliver value

4. **Write the post** following these rules:
   - Start with the hook — must work in 210 characters
   - Write in first person as Muhammad
   - Include specific details: product names (Amanda, Layla), markets (UAE, Malaysia), tools (Railway, Retell AI)
   - Mix sentence lengths aggressively
   - Use contractions naturally
   - Break every 1-2 sentences
   - End with a discussion-driving question
   - Add 3-5 specific hashtags

5. **Self-review** against the content-strategy quality checklist. Fix any issues before outputting.

6. **For carousels**, output:
   - Cover slide text (hook + title)
   - 8-10 content slides (1 key point per slide, max 30 words each)
   - CTA slide (follow prompt + discussion question)
   - Note: actual slide design is handled by visual-producer skill or delegate_task

7. **For video scripts**, output:
   - Hook (first 5 seconds — must stop the scroll)
   - Value delivery (30-60 seconds)
   - CTA (last 10 seconds)
   - Total target: 60-90 seconds
   - Include speaker notes / emphasis cues

## Output Format
Return the finished post in this structure:
```
POST TEXT:
[the actual post text, ready to copy-paste]

HASHTAGS:
#tag1 #tag2 #tag3

FORMAT: [text/image/carousel/video]

VISUAL BRIEF: [if image/carousel/video — describe the visual needed]

CAROUSEL SLIDES: [if carousel — slide-by-slide content]

VIDEO SCRIPT: [if video — timestamped script]

POSTING TIME: [recommended time, usually 7-9 AM ET]
```

## Pitfalls
- Don't default to list posts every time — rotate structures
- Don't start consecutive posts with the same pattern
- Don't write the hook as a question (questions as hooks underperform vs. bold statements)
- Don't use more than 3 emoji per post
- Don't mention competitors negatively — stay positive-constructive
- Don't write posts longer than 2000 characters unless it's a genuinely complex story

## Verification
Read the post aloud. If it sounds like a conference talk, rewrite it. If it sounds like a text message to a smart friend, ship it.
