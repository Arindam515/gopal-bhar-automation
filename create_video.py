import json, os, random, subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

ROOT = Path(__file__).parent
OUT = ROOT / "output"
TMP = OUT / "tmp"
ASSETS = ROOT / "assets"
STORIES = ROOT / "stories" / "stories.json"
W, H = 720, 1280
FPS = 24
SCENE_SECONDS = 12
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansBengaliUI-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
]

def font(size):
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def wrap_text(draw, text, fnt, max_width):
    words, lines, line = text.split(), [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=fnt)[2] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def draw_character(draw, x, y, name, scale=1.0):
    # Simple original vector cartoon fallback. Replace with your own licensed transparent PNGs for better results.
    r = int(90*scale)
    skin = "#E7B17B"
    draw.ellipse((x-r, y-r, x+r, y+r), fill=skin, outline="#38251C", width=max(2,int(5*scale)))
    # hair and moustache
    draw.pieslice((x-r-5, y-r-10, x+r+5, y+int(r*.2)), 180, 360, fill="#29201D")
    draw.ellipse((x-int(43*scale), y-int(15*scale), x-int(20*scale), y+int(8*scale)), fill="white")
    draw.ellipse((x+int(20*scale), y-int(15*scale), x+int(43*scale), y+int(8*scale)), fill="white")
    draw.ellipse((x-int(34*scale), y-int(8*scale), x-int(25*scale), y+int(2*scale)), fill="#171717")
    draw.ellipse((x+int(25*scale), y-int(8*scale), x+int(34*scale), y+int(2*scale)), fill="#171717")
    if name == "গোপাল":
        draw.arc((x-int(48*scale), y+int(5*scale), x+int(48*scale), y+int(55*scale)), 10, 170, fill="#38251C", width=max(3,int(8*scale)))
        draw.polygon([(x-int(48*scale),y+int(30*scale)),(x-int(10*scale),y+int(20*scale)),(x-int(2*scale),y+int(36*scale)),(x-int(30*scale),y+int(43*scale))], fill="#38251C")
        draw.polygon([(x+int(48*scale),y+int(30*scale)),(x+int(10*scale),y+int(20*scale)),(x+int(2*scale),y+int(36*scale)),(x+int(30*scale),y+int(43*scale))], fill="#38251C")
        draw.polygon([(x-r,y-r+5),(x+r,y-r+5),(x,y-r-int(100*scale))], fill="#B83A32", outline="#38251C")
    else:
        draw.arc((x-int(38*scale), y+int(5*scale), x+int(38*scale), y+int(45*scale)), 5, 175, fill="#38251C", width=max(3,int(5*scale)))
        draw.rectangle((x-r, y+r-5, x+r, y+r+int(105*scale)), fill="#D8A52D", outline="#38251C", width=max(2,int(4*scale)))
        draw.arc((x-r-int(20*scale),y-r-int(35*scale),x+r+int(20*scale),y-r+int(45*scale)),180,360,fill="#D8A52D",width=max(5,int(14*scale)))

def create_scene(scene, title, index, total):
    img = Image.new("RGB", (W,H), "#F5DDA8")
    d = ImageDraw.Draw(img)
    # palace / village background with simple shapes
    d.rectangle((0,0,W,780), fill="#F5DDA8")
    d.rectangle((0,780,W,H), fill="#C88D53")
    d.rectangle((30,180,W-30,740), fill="#F9EACB", outline="#8C4C2D", width=8)
    for xx in [95, 280, 465, 620]:
        d.rectangle((xx,230,xx+35,730), fill="#D7A96E", outline="#8C4C2D", width=4)
    d.rectangle((0,0,W,120), fill="#8B2F2F")
    d.text((W//2,60), title, font=font(34), fill="white", anchor="mm", stroke_width=1, stroke_fill="#411919")
    # alternating character placement for scene variation
    if scene.get("character","গোপাল") == "রাজা":
        draw_character(d, W//2, 485, "রাজা", 1.05)
    else:
        draw_character(d, W//2, 485, "গোপাল", 1.05)
    # subtitle panel
    d.rounded_rectangle((28,850,W-28,1190), radius=28, fill="#171717", outline="#F7D66A", width=5)
    lines = wrap_text(d, scene["dialogue"], font(38), W-100)
    y = 900
    for line in lines[:5]:
        d.text((W//2,y), line, font=font(38), fill="white", anchor="ma", stroke_width=1, stroke_fill="#000000")
        y += 58
    d.text((W//2,1230), f"দৃশ্য {index+1}/{total}", font=font(24), fill="#38251C", anchor="mm")
    path = TMP / f"scene_{index:02d}.png"
    img.save(path)
    return path

def run(cmd):
    subprocess.run(cmd, check=True)

def main():
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg is not installed on this runner.")
    OUT.mkdir(exist_ok=True); TMP.mkdir(exist_ok=True)
    for f in TMP.iterdir():
        if f.is_file(): f.unlink()
    stories = json.loads(STORIES.read_text(encoding="utf-8"))
    # Daily deterministic selection; can be overridden by STORY_INDEX secret/variable.
    index = int(os.getenv("STORY_INDEX", str((__import__("datetime").date.today().toordinal()) % len(stories)))) % len(stories)
    story = stories[index]
    scenes = story["scenes"]
    clips = []
    for i, scene in enumerate(scenes):
        image = create_scene(scene, story["title"], i, len(scenes))
        audio = TMP / f"voice_{i:02d}.mp3"
        clip = TMP / f"clip_{i:02d}.mp4"
        # gTTS is an unofficial free endpoint and may be rate-limited or change; failures stop the workflow.
        gTTS(text=scene["dialogue"], lang="bn", slow=False).save(str(audio))
        run([
            "ffmpeg","-y","-loop","1","-i",str(image),"-i",str(audio),
            "-vf",f"scale={W}:{H},zoompan=z='min(zoom+0.0008,1.04)':d={SCENE_SECONDS*FPS}:s={W}x{H}:fps={FPS},format=yuv420p",
            "-t",str(SCENE_SECONDS),"-r",str(FPS),"-c:v","libx264","-preset","ultrafast",
            "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k","-af","apad","-t",str(SCENE_SECONDS),str(clip)
        ])
        clips.append(clip)
    concat = TMP / "concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
    final = OUT / "gopal_bhar.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(final)])
    (OUT / "caption.txt").write_text(f"{story['title']}\nগোপাল ভাঁড়ের হাসির গল্প #গোপালভাঁড় #বাংলাকার্টুন #BanglaCartoon", encoding="utf-8")
    print(f"Created: {final}")
    print(f"Title: {story['title']}")

if __name__ == "__main__":
    main()
