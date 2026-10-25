# Gopal Bhar Free Cartoon Automation (MVP)

This is a free-first template-based cartoon video workflow for GitHub Actions. It creates a 30–60 second vertical MP4 from Bengali story dialogue, generates Bengali narration using gTTS, and optionally uploads the result to a Facebook Page through Meta's Page Videos API.

## Important limitations
- This is **not full generative AI animation**. It makes a lightly animated cartoon-style scene with zoom movement and captions. Replace the vector character with artwork you own or are licensed to use.
- gTTS relies on an unofficial endpoint and can be rate-limited or stop working.
- Meta API publishing requires your own Page ID, a valid Page access token, the necessary Page permissions and possibly app review. The script does not bypass Meta access controls.
- GitHub Actions scheduled jobs can start late. Public repository runner availability and policies can change.
- Avoid placing personal data or access tokens in public files. Use repository Actions secrets.

## Setup
1. Create a **public** GitHub repository and upload all files.
2. Go to Settings → Secrets and variables → Actions. Add:
   - `PAGE_ID`
   - `PAGE_ACCESS_TOKEN`
3. In Meta for Developers, configure a suitable app and obtain a Page token with the needed permissions, including `pages_manage_posts`, `pages_read_engagement`, and `pages_show_list`.
4. Open Actions → Create and publish Gopal Bhar cartoon → Run workflow to test manually.
5. If it succeeds, the schedule is 20:30 Bangladesh time (14:30 UTC).

## Files
- `stories/stories.json`: story dialogue. Add more stories here.
- `create_video.py`: renders the video.
- `publish_video.py`: uploads MP4 to the Page.
- `.github/workflows/daily-video.yml`: cloud schedule.

## Notes
The example story text is original demo content. Use artwork, music, voices, and stories you have rights to publish. The title/character may be based on folk tradition, but do not copy existing TV animation artwork or audio.
