---
name: visual-producer
description: Generates visual assets for LinkedIn posts — images, carousel PDFs, and video hooks using terminal tools (ImageMagick, wkhtmltoimage, ffmpeg).
version: 1.0.0
metadata:
  hermes:
    tags: [linkedin, visual, image, carousel, video, design]
    category: content
    requires_toolsets: [terminal]
---

# Visual Producer

## When to Use
When a LinkedIn post needs visual assets — a branded image, a carousel PDF, or a video hook. Called by the Content Strategist via delegate_task or directly during content production.

## Procedure

### Images (for image+text posts)

1. Generate a branded image using one of these approaches:

   **Option A — Text-overlay graphic (quote card, stat graphic):**
   ```bash
   # Use ImageMagick to create a branded graphic
   convert -size 1200x1200 \
     -background '#0a0a0a' \
     -fill '#ffffff' \
     -font 'Inter-Bold' \
     -pointsize 48 \
     -gravity Center \
     caption:"YOUR HEADLINE TEXT HERE" \
     ~/.hermes/data/linkedin-assets/post-$(date +%Y%m%d).png
   ```

   **Option B — AI-generated image (if API available):**
   Use the web toolset to call an image generation API (DALL-E, Midjourney API, etc.) if configured.

   **Option C — Screenshot/diagram:**
   Use terminal tools to capture or create technical diagrams.

2. **Image specs:**
   - Square: 1200x1200 (best engagement on LinkedIn)
   - Landscape: 1200x628 (alternative)
   - Format: PNG or JPG
   - Brand colors: Dark background (#0a0a0a), white text (#ffffff), accent blue (#0077B5)
   - Font: Inter, SF Pro, or system sans-serif

### Carousels (PDF documents)

1. Create an HTML file with slides:
   ```bash
   cat > /tmp/carousel.html << 'HTML'
   <!DOCTYPE html>
   <html>
   <head>
   <style>
     .slide { width: 1080px; height: 1080px; padding: 80px; box-sizing: border-box;
              background: #0a0a0a; color: #fff; font-family: 'Inter', sans-serif;
              display: flex; flex-direction: column; justify-content: center;
              page-break-after: always; }
     .slide h1 { font-size: 56px; line-height: 1.2; margin: 0 0 24px; }
     .slide p { font-size: 28px; line-height: 1.5; color: #b0b0b0; }
     .slide.cover { background: linear-gradient(135deg, #0a0a0a, #1a1a2e); }
     .slide.cover h1 { font-size: 64px; }
     .slide .number { font-size: 120px; font-weight: 900; color: #0077B5; margin-bottom: 24px; }
     .slide.cta { text-align: center; }
     .slide.cta h1 { color: #0077B5; }
   </style>
   </head>
   <body>
     <div class="slide cover">
       <h1>CAROUSEL TITLE</h1>
       <p>Subtitle / hook text</p>
     </div>
     <!-- Repeat for each content slide -->
     <div class="slide">
       <div class="number">1</div>
       <h1>First Point</h1>
       <p>Supporting detail in 1-2 sentences.</p>
     </div>
     <!-- ... more slides ... -->
     <div class="slide cta">
       <h1>Follow for more</h1>
       <p>What would you add to this list?</p>
     </div>
   </body>
   </html>
   HTML
   ```

2. Convert to PDF:
   ```bash
   # Using wkhtmltopdf or chrome headless
   wkhtmltopdf --page-width 1080 --page-height 1080 \
     --no-outline --disable-smart-shrinking \
     /tmp/carousel.html ~/.hermes/data/linkedin-assets/carousel-$(date +%Y%m%d).pdf
   ```

   Alternative with Chrome headless:
   ```bash
   google-chrome --headless --print-to-pdf=~/.hermes/data/linkedin-assets/carousel-$(date +%Y%m%d).pdf \
     --no-margins /tmp/carousel.html
   ```

3. **Carousel specs:**
   - 8-12 slides (including cover and CTA)
   - 1080x1080 per slide
   - Max 30 words per content slide
   - Cover slide: hook that makes people swipe
   - CTA slide: follow prompt + engagement question
   - Consistent brand template throughout

### Video Hooks

1. For text-overlay video (no face):
   ```bash
   # Create a 15-second hook video with text overlay using ffmpeg
   ffmpeg -f lavfi -i color=c=#0a0a0a:s=1080x1920:d=15 \
     -vf "drawtext=text='YOUR HOOK TEXT':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
     -c:v libx264 -pix_fmt yuv420p \
     ~/.hermes/data/linkedin-assets/video-$(date +%Y%m%d).mp4
   ```

2. **Video specs:**
   - 9:16 vertical (1080x1920) for maximum mobile engagement
   - Under 90 seconds total
   - First 3 seconds must hook — text overlay or dramatic opening
   - Native upload to LinkedIn (never a link)

## Asset Storage
All generated assets go to `~/.hermes/data/linkedin-assets/` with date-stamped filenames.

## Pitfalls
- wkhtmltopdf may not be installed — check first, fall back to Chrome headless
- ImageMagick `convert` might need `magick` on newer installs
- Ensure fonts are installed (Inter preferred, DejaVu Sans as fallback)
- LinkedIn compresses images aggressively — use high-res source (1200px+)

## Verification
Open the generated file and verify: readable text, correct dimensions, no clipping, brand-consistent colors.
