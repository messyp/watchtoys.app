#!/usr/bin/env python3
"""Builds index.html from the toy list below, so the fifteen sections of copy stay in one place.

    python3 tools/page.py            writes index.html, the site
    python3 tools/page.py preview    also writes raw/preview-buttons.html, the artifact version

index.html is what gets published. It has no build step on GitHub Pages; this script only saves
typing out five near-identical sections by hand.
"""
import html, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Every line here is checked against AppStore/LISTING.md in the app repo. See CLAIMS.md.
GROUPS = [
    dict(id="clack", name="Clack and knock", colour="#e8434f", toys=[
        dict(id="magnet", name="Magnet", free=True, hook="Steel that clacks and crackles.",
             body="Steel balls roll as you tilt and clack into chains. Touch the screen and they fly to your finger with crackling sparks. Let go and they scatter.",
             play="Tilt, and hold a finger"),
        dict(id="dominoes", name="Dominoes", free=False, hook="Tap one and the whole line goes.",
             body="They knock down the line one tick at a time. Turn the <span class=\"nb\">Digital Crown</span> to stand them back up.",
             play="Tap, then turn the <span class=\"nb\">Digital Crown</span>"),
        dict(id="cog", name="Cog", free=False, hook="Spin the brass wheel.",
             body="Turn the <span class=\"nb\">Digital Crown</span> to spin a brass wheel and send beads ricocheting round the screen.",
             play="Turn the <span class=\"nb\">Digital Crown</span>"),
    ]),
    dict(id="press", name="Pop and press", colour="#f08a24", toys=[
        dict(id="bath", name="Bath", free=False, hook="A bubble bath to push about.",
             body="Push the foam around, pop bubbles with a tap, and turn the <span class=\"nb\">Digital Crown</span> to run the tap.",
             play="Finger, tap and <span class=\"nb\">Digital Crown</span>"),
        dict(id="memory", name="Memory", free=False, hook="One more each round.",
             body="Ten bubbles glow in a pattern, like a handheld Pop It game. Tap it back. How long a sequence can you remember?",
             play="Tap"),
        dict(id="pop", name="Pop", free=True, hook="A popper that never runs out.",
             body="Push every dome through and a fresh sheet pops up straight away. Prefer bubble wrap? It's in Settings.",
             play="Tap")
    ]),
    dict(id="games", name="Tiny games", colour="#f2c531", toys=[
        dict(id="maze", name="Maze", free=True, hook="Roll the ball home.",
             body="Spin walnut labyrinths and stone castle keeps with the <span class=\"nb\">Digital Crown</span>. They get harder as you go.",
             play="Turn the <span class=\"nb\">Digital Crown</span>"),
        dict(id="trace", name="Trace", free=True, hook="25 shapes to follow.",
             body="Trace circles and stars, houses, numbers and mazes with your finger, each filling with colour, tick by tick.",
             play="Finger"),
        dict(id="bagatelle", name="Bagatelle", free=False, hook="A Victorian spring game.",
             body="Wind with the <span class=\"nb\">Digital Crown</span>, flick to fire, and score in the cups.",
             play="<span class=\"nb\">Digital Crown</span>, then flick"),
    ]),
    dict(id="pour", name="Tilt and pour", colour="#2aa8dc", toys=[
        dict(id="orbs", name="Orbs", free=True, hook="Hundreds of beads to pour and jab.",
             body="Glossy beads run from side to side as you tilt your wrist. Jab them with a finger and they go everywhere.",
             play="Tilt, and jab with a finger"),
        dict(id="liquid", name="Liquid", free=False, hook="Slosh the water about.",
             body="Tilt and it churns white where it breaks, with a little rowing boat riding on top. Flick the boat with a finger, or turn the <span class=\"nb\">Digital Crown</span> to rock the water into waves.",
             play="Tilt, finger and <span class=\"nb\">Digital Crown</span>"),
        dict(id="cascade", name="Cascade", free=False, hook="Open the gates.",
             body="Turn the <span class=\"nb\">Digital Crown</span> and the orbs go tumbling down a deep brass shaft.",
             play="Turn the <span class=\"nb\">Digital Crown</span>"),
    ]),
    dict(id="glow", name="Slow and glowing", colour="#9a5fe0", toys=[
        dict(id="smoke", name="Smoke", free=False, hook="A real fluid on your wrist.",
             body="Push wisps of smoke with a finger and they curl into eddies. Tap for a puff, or turn the <span class=\"nb\">Digital Crown</span> to stir a whirlpool.",
             play="Finger, tap and <span class=\"nb\">Digital Crown</span>"),
        dict(id="lava", name="Lava", free=False, hook="A lava lamp to squish.",
             body="Stir the glowing wax with your finger, and turn the <span class=\"nb\">Digital Crown</span> to turn up the heat.",
             play="Finger and <span class=\"nb\">Digital Crown</span>"),
        dict(id="fireworks", name="Fireworks", free=False, hook="Tap the night sky.",
             body="Send up a rocket. Peonies, rings, willows, palms and crackling chrysanthemums burst in colour and leave glowing smoke drifting over the stars.",
             play="Tap"),
    ]),
]

HERO_CLIP = "hero"   # tools/hero.swift cuts this from the toy clips
FREE_TAG = '<span class="tag">Free</span>'


def section_thumbs(g, flip):
    """One clip per section, and three picture buttons that plainly say what they do."""
    first = g["toys"][0]
    thumbs, copy = [], []
    for i, t in enumerate(g["toys"]):
        thumbs.append(
            f'<button class="thumb" type="button" aria-pressed="{"true" if i == 0 else "false"}" data-toy="{t["id"]}" '
            f'data-label="{html.escape(t["name"])} running on Apple Watch"><img src="assets/clips/{t["id"]}.jpg" alt="" width="211" height="257" loading="lazy">'
            f'<span class="thumb-name">{t["name"]}{FREE_TAG if t["free"] else ""}</span></button>')
        copy.append(f"""
      <div class="toy-copy" data-toy="{t["id"]}"{"" if i == 0 else " hidden"}>
        <p class="hook">{t["hook"]}</p>
        <p class="body">{t["body"]}</p>
        <p class="how">{t["play"]}</p>
      </div>""")
    return f"""
<section class="group thumbed{" flip" if flip else ""}" id="{g["id"]}" style="--t:{g["colour"]};--art:url(assets/clips/{first["id"]}.jpg)">
  <div class="group-in">
    <div class="group-text">
      <h2>{g["name"]}</h2>
      <div class="thumbs" role="group" aria-label="Choose a toy to see">{"".join(thumbs)}</div>{"".join(copy)}
    </div>
    <figure class="screen"><video data-src="assets/clips/{first["id"]}.mp4" poster="assets/clips/{first["id"]}.jpg" muted loop playsinline preload="none" width="422" height="514" aria-label="{first["name"]} running on Apple Watch"></video></figure>
  </div>
</section>"""


STYLE = '''
@font-face{font-family:"Bricolage Grotesque";font-weight:200 800;font-style:normal;font-display:swap;src:url(assets/fonts/bricolage-grotesque.woff2) format("woff2")}
@font-face{font-family:"Instrument Sans";font-weight:400 700;font-style:normal;font-display:swap;src:url(assets/fonts/instrument-sans.woff2) format("woff2")}
/* Layout: the bezel hero, then five coloured sections of three toys each. */
:root{
  --ground:#0b0b15; --panel:#12121f; --line:#2c2c3c;
  --text:#f6f4fb; --dim:#aaa9bf; --cyan:#35d4ee; --violet:#8a5cf6; --magenta:#ef3fb0;
  --display:"Bricolage Grotesque",system-ui,sans-serif;
  --body:"Instrument Sans",ui-sans-serif,system-ui,sans-serif;
  --gutter-l:max(20px,env(safe-area-inset-left,0px));
  --gutter-r:max(20px,env(safe-area-inset-right,0px));
  color-scheme:dark;
}
*{box-sizing:border-box}
html{background:var(--ground)}
body{margin:0;background:var(--ground);color:var(--text);font:500 17.5px/1.55 var(--body);-webkit-font-smoothing:antialiased;overflow-x:clip}
img,video,svg{display:block;max-width:100%}
a{color:inherit}
h1,h2,p,ul,dl,dd,figure{margin:0}
:focus-visible{outline:2px solid var(--cyan);outline-offset:3px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.nb{white-space:nowrap}
.wrap{width:100%;max-width:1200px;margin-inline:auto;padding-left:var(--gutter-l);padding-right:var(--gutter-r)}
h2{font:700 clamp(34px,4.4vw,58px)/1.04 var(--display);letter-spacing:-.025em;text-wrap:balance}

/* A glossy bead, in the colours of the app's icon. */
.bead{display:inline-block;border-radius:50%;background:
  radial-gradient(circle at 34% 28%,#fff 0 7%,#ffffffb0 13%,transparent 30%),
  radial-gradient(circle at 42% 38%,#6fe9f7,#4f7df0 46%,#8a4fe8 74%,#d63fbe 100%)}

/* Hero */
.hero{position:relative;isolation:isolate;padding-block:clamp(28px,4.4vw,64px);border-bottom:1px solid var(--line)}
.hero::before{content:"";position:absolute;inset:0;z-index:-1;
  background:radial-gradient(52% 70% at 12% 8%,#8a5cf626,transparent 70%),radial-gradient(40% 60% at 42% 96%,#ef3fb014,transparent 72%)}
.hero-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,372px);gap:clamp(24px,5vw,80px);align-items:center}
.hero-main{display:grid;gap:clamp(18px,2.2vw,26px);justify-items:start;min-width:0}
.logo{display:inline-flex;align-items:center;font:700 clamp(26px,2.6vw,32px)/1 var(--display);letter-spacing:-.02em}
.logo img{width:1.7em;height:1.7em;border-radius:50%;margin-right:.42em}
.headline{font:700 clamp(50px,7.6vw,104px)/.98 var(--display);letter-spacing:-.035em;text-wrap:balance}
.sub{color:var(--dim);font-size:clamp(18px,1.55vw,21px);max-width:42ch}
.soon{display:inline-flex;align-items:center;gap:10px;padding:13px 22px 13px 16px;border:1px solid #ffffff2e;border-radius:999px;font:500 clamp(17px,1.5vw,19px)/1.1 var(--display);background:#ffffff0d}
.soon .bead{width:16px;height:16px;flex:none}

/* Apple's bezel, used as is: no crop, tilt, shadow or overlay. The opening is 422x514 at (99,213) of 620x940. */
.device{position:relative;width:100%;aspect-ratio:620/940}
.device video{position:absolute;left:15.97%;top:22.66%;width:68.06%;height:54.68%;object-fit:cover;background:#000}
.device img{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}

.tag{display:inline-block;font:700 10.5px/1 var(--body);letter-spacing:.05em;text-transform:uppercase;padding:3px 5px 3px;border-radius:5px;background:#fff;color:#14141f}

/* Quiet */
.quiet{padding-block:clamp(64px,9vw,120px);border-bottom:1px solid var(--line)}
.quiet p{font:600 clamp(30px,4.6vw,60px)/1.12 var(--display);letter-spacing:-.025em;max-width:20ch;text-wrap:balance}
.quiet span{color:var(--dim)}

/* Toy sections */
.group{position:relative;isolation:isolate;overflow:clip;padding-block:clamp(44px,6vw,84px);scroll-margin-top:12px}
.group+.group{border-top:1px solid var(--line)}
.group::before{content:"";position:absolute;inset:-12%;z-index:-1;background:var(--art) center/120% auto;filter:blur(90px) saturate(1.5);opacity:.26;transition:background-image .4s}
.group::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(var(--ground),transparent 24%,transparent 76%,var(--ground))}
.group-in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,400px);gap:clamp(32px,7vw,110px);max-width:1120px;margin-inline:auto;padding-left:var(--gutter-l);padding-right:var(--gutter-r);align-items:center}
.flip .group-in{grid-template-columns:minmax(0,400px) minmax(0,1fr)}
.flip .screen{grid-row:1;grid-column:1}
.flip .group-text{grid-column:2}
.group-text{display:grid;gap:20px;min-width:0}
.group h2{color:var(--t);filter:brightness(1.16)}
.thumbs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;max-width:420px}
.thumb{appearance:none;display:grid;gap:8px;justify-items:center;background:none;border:0;padding:0;color:var(--dim);font:500 17px/1.1 var(--display);cursor:pointer;-webkit-tap-highlight-color:transparent}
.thumb img{width:100%;height:auto;aspect-ratio:422/514;object-fit:cover;border-radius:15%/12.4%;opacity:.62;box-shadow:0 0 0 1px #ffffff2e;transition:opacity .15s,box-shadow .15s}
.thumb-name{display:inline-flex;align-items:center;gap:6px}
.thumb:hover img{opacity:.9}
.thumb[aria-pressed="true"]{color:var(--text)}
.thumb[aria-pressed="true"] img{opacity:1;box-shadow:0 0 0 3px var(--ground),0 0 0 6px var(--t)}
.toy-copy{display:grid;gap:12px;min-width:0}
.toy-copy[hidden]{display:none}
.hook{font:600 clamp(25px,2.6vw,34px)/1.1 var(--display);letter-spacing:-.02em}
.body{color:#d9d8e6;max-width:46ch}
.how{color:var(--dim);font-size:16px}
.how::before{content:"How you play: "}
.screen{aspect-ratio:422/514;border-radius:15%/12.4%;overflow:hidden;background:#000;box-shadow:0 0 0 1px #ffffff26,0 24px 70px -20px color-mix(in srgb,var(--t) 50%,transparent)}
.screen video{width:100%;height:100%;object-fit:cover}

/* Film slot: commented out in the page until the wrist film exists. */
.film{padding-block:clamp(44px,6vw,88px);border-bottom:1px solid var(--line)}
.film .wrap{display:grid;gap:clamp(20px,3vw,32px)}
.film video{width:100%;height:auto;aspect-ratio:1920/824;border-radius:clamp(12px,1.6vw,20px);background:#000}

/* How it feels */
.feel{padding-block:clamp(56px,8vw,108px);background:var(--panel);border-top:1px solid var(--line)}
.moves{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(24px,3.4vw,48px);margin-top:clamp(28px,4vw,48px)}
.move{display:grid;gap:10px;align-content:start;min-width:0}
.move h3{margin:0;font:600 clamp(22px,2.1vw,27px)/1.1 var(--display)}
.move p{color:#d9d8e6;max-width:34ch}
.move .uses{color:var(--dim);font-size:15.5px}
.settings{margin-top:clamp(28px,4vw,44px);padding-top:18px;border-top:1px solid #ffffff1f;color:var(--dim)}

/* The deal */
.deal{padding-block:clamp(64px,9vw,116px);background:radial-gradient(70% 90% at 50% 100%,#8a5cf626,transparent 72%);border-top:1px solid var(--line)}
.deal .wrap{display:grid;justify-items:center;gap:22px;text-align:center}
.deal p{color:#d9d8e6;max-width:56ch}
.promises{list-style:none;padding:0;display:flex;flex-wrap:wrap;justify-content:center;gap:10px 28px;font:500 clamp(19px,2vw,24px)/1.2 var(--display)}
.promises li{display:inline-flex;align-items:center;gap:9px}
.promises .bead{width:13px;height:13px}
.req{color:var(--dim);font-size:15.5px}

/* Footer */
.foot{padding-block:32px 44px;border-top:1px solid var(--line)}
.foot .wrap{display:grid;gap:14px}
.foot-links{display:flex;flex-wrap:wrap;gap:8px 24px}
.foot-links a{color:var(--dim);text-underline-offset:3px}
.foot-links a:hover{color:var(--text)}
.legal{color:#8a899e;font-size:13.5px;max-width:92ch}
.foot .wrap{grid-template-columns:minmax(0,1fr) auto;align-items:end;gap:20px clamp(24px,5vw,64px)}
.foot-main{display:grid;gap:14px;min-width:0}
.maker{display:block;transition:transform .2s}
.maker:hover{transform:rotate(2deg) scale(1.04)}
.maker img{display:block;width:clamp(170px,16vw,214px);height:auto}

@media (max-width:900px){
  .foot .wrap{grid-template-columns:minmax(0,1fr)}
  .maker{justify-self:start}
  body{font-size:17px}
  .hero-row{grid-template-columns:minmax(0,1fr);gap:30px}
  .hero .device{width:min(84%,330px);justify-self:center}
  .group-in,.flip .group-in{grid-template-columns:minmax(0,1fr)}
  .flip .screen,.flip .group-text{grid-row:auto;grid-column:auto}
  .group .screen{width:min(84%,340px);justify-self:center}
  .thumbed .group-text{display:contents}
  .thumbed h2{order:1}.thumbed .screen{order:2}.thumbed .thumbs{order:3;width:100%;justify-self:center}.thumbed .toy-copy{order:4}
  .moves{grid-template-columns:minmax(0,1fr)}
  .film video{aspect-ratio:4/3;object-fit:cover}
}
'''

SCRIPT = '''
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

// Only the video nearest the middle of the screen plays. Clips load when they're needed and are
// released when they leave, because phones limit how many videos a page can hold open.
const vids = [...document.querySelectorAll('video')];
const film = document.querySelector('.film video');
const load = v => { if (!v.src && v.dataset.src) v.src = v.dataset.src; };
const release = v => { if (v !== film && v.src) { v.removeAttribute('src'); v.load(); } };

if (calm) {
  vids.forEach(v => { v.controls = true; });
  const near = new IntersectionObserver(entries => {
    for (const e of entries) if (e.isIntersecting) load(e.target);
  }, { rootMargin: '400px 0px' });
  vids.forEach(v => near.observe(v));
}

// Someone who pauses the film themselves stays in charge of it until they play it again.
let filmHeld = false, ourPause = false;
if (film) {
  film.addEventListener('pause', () => { if (ourPause) ourPause = false; else if (!film.ended && !document.hidden) filmHeld = true; });
  film.addEventListener('play', () => { filmHeld = false; });
}

const pickClip = () => {
  queued = false;
  if (calm) return;
  const middle = innerHeight / 2;
  let best = null, gap = Infinity;
  for (const v of vids) {
    const r = v.getBoundingClientRect();
    const seen = Math.min(r.bottom, innerHeight) - Math.max(r.top, 0);
    if (seen < r.height * 0.5) continue;
    const d = Math.abs((r.top + r.bottom) / 2 - middle);
    if (d < gap) { best = v; gap = d; }
  }
  for (const v of vids) {
    if (v === best) continue;
    if (!v.paused) { if (v === film) ourPause = true; v.pause(); }
    release(v);
  }
  if (best && best.paused && !(best === film && filmHeld)) {
    load(best);
    if (best !== film) best.muted = true;
    best.play().catch(() => {});
  }
};
let queued = false;
const queuePick = () => { if (!queued) { queued = true; requestAnimationFrame(pickClip); } };
addEventListener('scroll', queuePick, { passive: true });
addEventListener('resize', queuePick);
addEventListener('touchend', queuePick, { passive: true });
setInterval(queuePick, 1000);
pickClip();

// The picture buttons swap a section's one video, so it never holds two clips.
const choose = (section, toy) => {
  const v = section.querySelector('video');
  section.querySelectorAll('.thumb').forEach(b => {
    const on = b.dataset.toy === toy;
    b.setAttribute('aria-pressed', on);
    if (on) v.setAttribute('aria-label', b.dataset.label);
  });
  section.querySelectorAll('.toy-copy').forEach(c => { c.hidden = c.dataset.toy !== toy; });
  v.pause();
  v.removeAttribute('src');
  v.load();
  v.dataset.src = `assets/clips/${toy}.mp4`;
  v.poster = `assets/clips/${toy}.jpg`;
  section.style.setProperty('--art', `url(assets/clips/${toy}.jpg)`);
  if (calm) load(v); else queuePick();
};
document.querySelectorAll('.thumb').forEach(b => b.addEventListener('click', () => choose(b.closest('.group'), b.dataset.toy)));

'''

LOGO = '<span class="logo" aria-hidden="true"><img src="assets/logo.png" alt="" width="78" height="78">Watch&nbsp;Toys</span>'
SOON = '<p class="soon"><i class="bead" aria-hidden="true"></i>Coming soon to the App Store</p>'
BEAD = '<i class="bead" aria-hidden="true"></i>'

BODY = f'''<header class="hero">
  <div class="wrap">
    <h1 class="sr">Watch Toys: Fidget &amp; Games</h1>
    <div class="hero-row">
      <div class="hero-main">
        {LOGO}
        <p class="headline">Something to do with your hands.</p>
        <p class="sub">Fifteen tactile toys and tiny games for <span class="nb">Apple Watch</span>, each made to be felt as much as seen.</p>
        {SOON}
      </div>
      <figure class="device"><video id="device" data-src="assets/clips/{HERO_CLIP}.mp4" poster="assets/clips/{HERO_CLIP}.jpg" muted loop playsinline preload="none" width="422" height="514" aria-label="Watch Toys running on Apple Watch"></video><img src="assets/apple-watch-ultra-4.png" alt="" width="620" height="940"></figure>
    </div>
  </div>
</header>

<main>
<!--FILM (remove this comment's markers once assets/film exists)
<section class="film">
  <div class="wrap">
    <h2>On a real wrist</h2>
    <video data-src="assets/film/film.mp4" poster="assets/film/poster.jpg" muted loop playsinline controls preload="none" width="1920" height="824" aria-label="Watch Toys being played on a wrist"></video>
  </div>
</section>
/FILM-->

<section class="quiet">
  <div class="wrap"><p>Quiet enough for a meeting. <span>Quick enough for a queue.</span></p></div>
</section>
<!--SECTIONS-->

<section class="feel" id="feel">
  <div class="wrap">
    <h2>Made to be felt as much as seen</h2>
    <div class="moves">
      <div class="move">
        <h3>Tilt your wrist</h3>
        <p>Pour the beads, roll the steel, slosh the water.</p>
        <p class="uses">Magnet, Orbs, Liquid</p>
      </div>
      <div class="move">
        <h3>Use your finger</h3>
        <p>Jab the beads, pop the domes, push the smoke.</p>
        <p class="uses">Orbs, Magnet, Pop, Smoke, Lava, Bath, Trace, Fireworks, Dominoes, Memory</p>
      </div>
      <div class="move">
        <h3>Turn the <span class="nb">Digital Crown</span></h3>
        <p>Spin the maze, wind the spring, open the gates.</p>
        <p class="uses">Maze, Bagatelle, Cascade, Cog</p>
      </div>
    </div>
    <p class="settings">Steel balls clack with a click through your wrist, and bubbles pop under your finger. Haptic strength, colours, sizes and more are in Settings.</p>
  </div>
</section>

<section class="deal" id="get">
  <div class="wrap">
    <h2>Five toys free. One purchase for the rest.</h2>
    <p>Try each locked toy free, twice, for a minute at a time. One purchase unlocks them all, plus every toy added later. Family Sharing included.</p>
    <ul class="promises">
      <li>{BEAD}No ads</li><li>{BEAD}No subscription</li><li>{BEAD}No account</li><li>{BEAD}No data collected</li>
    </ul>
    {SOON}
    <p class="req">Requires <span class="nb">Apple Watch</span>.</p>
  </div>
</section>
</main>

<footer class="foot">
  <div class="wrap">
    <div class="foot-main">
    {LOGO}
    <nav class="foot-links" aria-label="Footer"><a href="https://beautifuldistraction.com/watch-toys/">Support</a><a href="https://beautifuldistraction.com/watch-toys/privacy/">Privacy policy</a><a href="https://beautifuldistraction.com/">Beautiful Distraction</a></nav>
    <p class="legal">© 2026 Beautiful Distraction. Watch Toys is not made or endorsed by Apple. Apple, the Apple logo, <span class="nb">Apple Watch</span>, <span class="nb">Apple Watch Ultra</span> and <span class="nb">Digital Crown</span> are trademarks of Apple Inc., registered in the U.S. and other countries. App Store is a service mark of Apple Inc., registered in the U.S. and other countries.</p>
    <p class="legal">This site uses no cookies or analytics.</p>
    </div>
    <a class="maker" href="https://beautifuldistraction.com/"><img src="assets/beautiful-distraction.png" alt="Beautiful Distraction" width="213" height="89"></a>
  </div>
</footer>
'''

SITE = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Watch Toys</title>
<meta name="description" content="Fifteen tactile toys and tiny games for Apple Watch. Coming soon to the App Store.">
<meta name="robots" content="noindex">
<link rel="icon" href="assets/icon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/icon.png">
<meta property="og:title" content="Watch Toys">
<meta property="og:description" content="Something to do with your hands.">
<meta property="og:url" content="https://watchtoys.app/">
<style>{STYLE}</style>
</head>
<body>
{BODY}<script>{SCRIPT}</script>
</body>
</html>
'''

SECTIONS = "".join(section_thumbs(g, i % 2 == 1) for i, g in enumerate(GROUPS))

(ROOT / "index.html").write_text(SITE.replace("<!--SECTIONS-->", SECTIONS))
print("index.html", len(SITE))

if len(sys.argv) > 1 and sys.argv[1] == "preview":
    # The artifact wraps its own document skeleton round the page.
    body = BODY
    page = f'''<title>Watch Toys Buttons</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>{STYLE}</style>
{body.replace("<!--SECTIONS-->", SECTIONS)}<script>{SCRIPT}</script>
'''
    (ROOT / "raw" / "preview-buttons.html").write_text(page)
    print("raw/preview-buttons.html", len(page))
