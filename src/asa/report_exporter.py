from __future__ import annotations

import html
import shutil
from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json, write_text
from .quality.report import quality_report_for_run
from .review_summary import summarize_run_reviews


REPORT_CSS = """
:root {
  color-scheme: dark;
  --bg: #090a0f;
  --ink: #f4efe4;
  --muted: #a29b90;
  --line: rgba(244, 239, 228, 0.13);
  --accent: #e8ff7a;
  --accent-2: #7ce6d3;
  --accent-3: #8c6dff;
  --warn: #ff9f68;
  --title-gradient: linear-gradient(110deg, var(--ink) 0%, var(--ink) 58%, rgba(232,255,122,0.88) 78%, rgba(124,230,211,0.74) 100%);
  --font: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 132px; }
body { margin: 0; color: var(--ink); background: radial-gradient(circle at 4% 0%, rgba(140,109,255,.24), transparent 28rem), radial-gradient(circle at 96% 24%, rgba(124,230,211,.16), transparent 30rem), linear-gradient(180deg, rgba(255,255,255,.025), transparent 24rem), var(--bg); font-family: var(--font); line-height: 1.6; }
body::before { position: fixed; inset: 0; z-index: -1; pointer-events: none; content: ""; background-image: linear-gradient(rgba(244,239,228,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(244,239,228,.035) 1px, transparent 1px); background-size: 44px 44px; mask-image: linear-gradient(to bottom, rgba(0,0,0,.72), transparent 78%); }
a { color: inherit; text-decoration: none; }
code { font-family: var(--mono); }
.shell { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 34px 0 56px; }
.topbar { position: sticky; top: 16px; z-index: 10; display: flex; justify-content: space-between; gap: 18px; align-items: center; margin-bottom: 28px; padding: 10px 10px 10px 14px; border: 1px solid var(--line); border-radius: 999px; background: rgba(9,10,15,.72); backdrop-filter: blur(18px); }
.brand { display: flex; gap: 10px; align-items: center; color: var(--ink); font-weight: 720; letter-spacing: -.03em; }
.brand::before { display: none; }
.brand-mark { width: 12px; height: 12px; border-radius: 999px; background: var(--accent); box-shadow: 0 0 28px rgba(232,255,122,.72); }
.brand-text { white-space: nowrap; }
.nav { display: flex; flex-wrap: wrap; gap: 4px; color: var(--muted); font-size: .9rem; }
.nav a { padding: 8px 11px; border: 1px solid transparent; border-radius: 999px; }
.nav a:hover { color: var(--ink); border-color: var(--line); background: rgba(244,239,228,.06); }
.hero, .section { position: relative; overflow: hidden; border: 1px solid var(--line); border-radius: 32px; background: linear-gradient(145deg, rgba(246,241,228,.08), rgba(246,241,228,.025)); box-shadow: 0 40px 120px rgba(0,0,0,.28); }
.hero { padding: 44px; }
.hero::after { position: absolute; right: -8rem; top: -8rem; width: 22rem; height: 22rem; border-radius: 999px; content: ""; background: radial-gradient(circle, rgba(124,230,211,.14), transparent 66%); filter: blur(8px); }
.label { margin: 0 0 16px; color: var(--accent-2); font-family: var(--mono); font-size: .72rem; font-weight: 680; letter-spacing: .12em; text-transform: uppercase; }
h1 { max-width: 980px; margin: 0; color: transparent; background: var(--title-gradient); background-clip: text; -webkit-background-clip: text; font-size: clamp(3rem, 8vw, 7.2rem); line-height: .92; letter-spacing: -.08em; }
h2 { margin: 0 0 18px; color: transparent; background: var(--title-gradient); background-clip: text; -webkit-background-clip: text; font-size: clamp(1.8rem, 3.4vw, 3.2rem); line-height: 1.02; letter-spacing: -.064em; }
h3 { margin: 0 0 10px; font-size: 1.08rem; letter-spacing: -.03em; }
.muted { color: var(--muted); }
.grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 22px; }
.stat, .card, .section { border: 1px solid var(--line); border-radius: 22px; background: rgba(0,0,0,.18); }
.stat { min-height: 124px; padding: 18px; transition: transform .22s ease, border-color .22s ease; }
.stat:hover { transform: translateY(-3px); border-color: rgba(232,255,122,.3); }
.stat span { display: block; color: var(--muted); font-family: var(--mono); font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; }
.stat strong { display: block; margin-top: 16px; font-size: clamp(1.7rem, 3vw, 2.4rem); line-height: 1; }
.section { margin-top: 18px; padding: 28px; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.card { padding: 18px; }
.card p { margin: 0; color: var(--muted); }
.list { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.list li { padding: 13px 14px; border: 1px solid var(--line); border-radius: 16px; background: rgba(246,241,228,.035); }
.pill { display: inline-flex; align-items: center; padding: 4px 8px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); font-family: var(--mono); font-size: .72rem; }
.ok { color: var(--accent-2); }
.bad { color: var(--warn); }
.table { width: 100%; border-collapse: collapse; overflow: hidden; border: 1px solid var(--line); border-radius: 18px; }
.table th, .table td { padding: 13px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
.table th { color: var(--muted); font-family: var(--mono); font-size: .72rem; letter-spacing: .09em; text-transform: uppercase; }
.table tr:last-child td { border-bottom: 0; }
.mono { font-family: var(--mono); font-size: .86rem; }
.footer { margin-top: 26px; color: var(--muted); font-family: var(--mono); font-size: .76rem; }

.report-hero { padding: clamp(30px, 5vw, 56px); }
.hero-grid { position: relative; z-index: 1; display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: clamp(20px, 3vw, 34px); align-items: stretch; }
.report-kicker { position: relative; display: inline-grid; width: fit-content; min-width: 190px; gap: 5px; margin: 0 0 clamp(20px, 3vw, 34px); padding: 12px 15px 12px 17px; border: 1px solid rgba(244,239,228,.12); border-left-color: rgba(232,255,122,.58); border-radius: 18px; background: linear-gradient(135deg, rgba(232,255,122,.085), rgba(124,230,211,.035) 46%, rgba(0,0,0,.16)), rgba(0,0,0,.2); box-shadow: inset 0 1px 0 rgba(255,255,255,.04), 0 16px 38px rgba(0,0,0,.16); overflow: hidden; }
.report-kicker::before { position: absolute; top: 12px; bottom: 12px; left: 0; width: 2px; border-radius: 999px; content: ""; background: linear-gradient(180deg, var(--accent), rgba(124,230,211,.4)); box-shadow: 0 0 20px rgba(232,255,122,.48); }
.report-kicker::after { position: absolute; inset: 0; content: ""; background: linear-gradient(100deg, transparent 0%, rgba(244,239,228,.08) 46%, transparent 70%); transform: translateX(-120%); animation: labelScan 5.6s ease-in-out infinite; }
.report-kicker span, .report-kicker strong, .report-kicker i { position: relative; z-index: 1; }
.report-kicker span { color: rgba(124,230,211,.78); font-family: var(--font); font-size: .72rem; font-weight: 720; letter-spacing: .1em; line-height: 1; text-transform: uppercase; }
.report-kicker strong { color: rgba(244,239,228,.92); font-family: var(--font); font-size: .98rem; font-weight: 770; letter-spacing: -.026em; line-height: 1.16; }
.report-kicker i { position: absolute; right: 13px; top: 14px; width: 6px; height: 6px; border-radius: 999px; background: var(--accent); box-shadow: 0 0 18px rgba(232,255,122,.72); }
@keyframes labelScan { 0%, 54% { transform: translateX(-120%); } 72%, 100% { transform: translateX(120%); } }
.hero-lede { max-width: 720px; margin: 22px 0 0; color: rgba(244,239,228,.68); font-size: clamp(1rem, 1.55vw, 1.18rem); font-weight: 520; line-height: 1.78; letter-spacing: -.015em; }
.run-meta { display: grid; width: min(100%, 720px); grid-template-columns: minmax(0, 1fr) auto auto; gap: 0; margin-top: 24px; overflow: hidden; border: 1px solid rgba(244,239,228,.12); border-radius: 18px; background: linear-gradient(135deg, rgba(246,241,228,.055), rgba(246,241,228,.018)); box-shadow: inset 0 1px 0 rgba(255,255,255,.035); }
.meta-item { display: grid; gap: 5px; min-width: 0; padding: 12px 14px; border-right: 1px solid rgba(244,239,228,.09); }
.meta-item:last-child { min-width: 142px; border-right: 0; background: linear-gradient(135deg, rgba(232,255,122,.07), rgba(124,230,211,.025)); }
.meta-label { color: rgba(124,230,211,.68); font-family: var(--mono); font-size: .68rem; font-weight: 730; letter-spacing: .11em; line-height: 1; text-transform: uppercase; }
.meta-value { min-width: 0; color: rgba(244,239,228,.86); font-family: var(--font); font-size: .9rem; font-weight: 680; letter-spacing: -.018em; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta-value.mono { font-family: var(--mono); font-size: .8rem; letter-spacing: .015em; }
.meta-value.ok { color: var(--accent); }
.meta-value.bad { color: var(--warn); }
.run-kind-chip { display: inline-flex; width: fit-content; align-items: center; gap: 7px; padding: 5px 8px; border: 1px solid rgba(244,239,228,.12); border-radius: 999px; color: rgba(244,239,228,.82); background: rgba(246,241,228,.045); font: 760 .72rem/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; }
.run-kind-chip::before { width: 7px; height: 7px; border-radius: 999px; content: ""; background: var(--accent-2); box-shadow: 0 0 14px rgba(124,230,211,.42); }
.run-kind-chip[data-run-kind="demo fixture"] { border-color: rgba(255,159,104,.2); color: rgba(255,190,143,.92); background: rgba(255,159,104,.055); }
.run-kind-chip[data-run-kind="demo fixture"]::before { background: var(--warn); box-shadow: 0 0 14px rgba(255,159,104,.42); }
.run-kind-chip[data-run-kind="mock run"] { border-color: rgba(155,140,255,.22); color: #c8c0ff; background: rgba(155,140,255,.055); }
.run-kind-chip[data-run-kind="mock run"]::before { background: var(--accent-3); box-shadow: 0 0 14px rgba(155,140,255,.42); }
.run-kind-chip[data-run-kind="real run"] { border-color: rgba(124,230,211,.25); color: rgba(124,230,211,.94); background: rgba(124,230,211,.06); }
.verdict-card { display: grid; min-height: 260px; grid-template-rows: auto 1fr auto; gap: 18px; padding: 22px; border: 1px solid rgba(232,255,122,.24); border-radius: 24px; background: radial-gradient(circle at 100% 0%, rgba(232,255,122,.15), transparent 16rem), linear-gradient(145deg, rgba(232,255,122,.045), rgba(0,0,0,.2)); }
.verdict-card .eyebrow-label { color: rgba(232,255,122,.72); font-family: var(--mono); font-size: .7rem; font-weight: 720; letter-spacing: .12em; text-transform: uppercase; }
.verdict-card .status-copy { align-self: center; display: block; color: var(--accent); font-size: clamp(2.05rem, 4vw, 3.35rem); font-weight: 790; line-height: .95; letter-spacing: -.065em; }
.verdict-card .micro-copy { margin: 0; color: rgba(244,239,228,.66); font-size: .92rem; font-weight: 560; line-height: 1.7; letter-spacing: -.01em; }
.archive-brief { display: grid; align-content: start; gap: 18px; min-height: 260px; padding: 22px; border: 1px solid rgba(244,239,228,.13); border-radius: 24px; background: radial-gradient(circle at 100% 0%, rgba(124,230,211,.12), transparent 15rem), linear-gradient(145deg, rgba(246,241,228,.055), rgba(0,0,0,.18)); box-shadow: inset 0 1px 0 rgba(255,255,255,.035); }
.archive-brief .eyebrow-label { margin-bottom: 0; color: rgba(124,230,211,.72); font-family: var(--font); letter-spacing: .095em; }
.archive-brief ul { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
.archive-brief li { display: flex; justify-content: space-between; gap: 14px; align-items: center; padding: 11px 12px; border: 1px solid rgba(244,239,228,.095); border-radius: 15px; background: rgba(0,0,0,.15); }
.archive-brief li span { color: rgba(244,239,228,.54); font-size: .78rem; font-weight: 690; letter-spacing: .02em; }
.archive-brief li strong { color: rgba(244,239,228,.88); font-size: .9rem; font-weight: 730; letter-spacing: -.018em; }
.archive-brief li strong.ok { color: var(--accent); }
.archive-brief li strong.bad { color: var(--warn); }
.archive-brief .micro-copy { margin: 0; color: rgba(244,239,228,.62); font-size: .88rem; font-weight: 540; line-height: 1.65; }
.channel-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.channel-card { --channel-color: var(--accent); position: relative; display: flex; min-height: 220px; flex-direction: column; justify-content: space-between; padding: 20px; border: 1px solid color-mix(in srgb, var(--channel-color) 24%, var(--line)); border-radius: 22px; background: radial-gradient(circle at 100% 0%, color-mix(in srgb, var(--channel-color) 14%, transparent), transparent 12rem), linear-gradient(145deg, rgba(246,241,228,.055), rgba(246,241,228,.022)); transition: transform .22s ease, border-color .22s ease, background .22s ease; }
.channel-card:hover { transform: translateY(-4px); border-color: color-mix(in srgb, var(--channel-color) 42%, var(--line)); background: radial-gradient(circle at 100% 0%, color-mix(in srgb, var(--channel-color) 18%, transparent), transparent 12rem), linear-gradient(145deg, rgba(246,241,228,.07), rgba(246,241,228,.026)); }
.channel-card > span { width: fit-content; padding: 5px 8px; border: 1px solid color-mix(in srgb, var(--channel-color) 32%, var(--line)); border-radius: 999px; color: var(--channel-color); background: color-mix(in srgb, var(--channel-color) 8%, transparent); font-family: var(--mono); font-size: .68rem; font-weight: 720; letter-spacing: .1em; text-transform: uppercase; }
.channel-card strong { display: block; margin-top: 34px; color: color-mix(in srgb, var(--channel-color) 34%, var(--ink)); font-size: 1.22rem; font-weight: 760; letter-spacing: -.04em; }
.channel-card p { margin: 10px 0 0; color: rgba(244,239,228,.62); font-size: .94rem; font-weight: 510; line-height: 1.68; }
.channel-disabled { cursor: default; filter: saturate(.82); }
.channel-disabled::after { position: absolute; right: 18px; bottom: 18px; width: 8px; height: 8px; border-radius: 999px; content: ""; background: color-mix(in srgb, var(--channel-color) 72%, var(--ink)); box-shadow: 0 0 18px color-mix(in srgb, var(--channel-color) 32%, transparent); opacity: .78; }
.channel-disabled > span { border-style: dashed; color: color-mix(in srgb, var(--channel-color) 70%, var(--muted)); background: color-mix(in srgb, var(--channel-color) 6%, rgba(0,0,0,.14)); }
.feature-card { min-height: 150px; }

.snapshot-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(340px, .85fr); gap: 14px; }
.snapshot-card { padding: 20px; border: 1px solid rgba(244,239,228,.105); border-radius: 24px; background: radial-gradient(circle at 100% 0%, rgba(124,230,211,.08), transparent 14rem), linear-gradient(145deg, rgba(246,241,228,.052), rgba(0,0,0,.16)); }
.snapshot-card h3 { margin: 0; color: rgba(244,239,228,.94); font-size: clamp(1.45rem, 2.2vw, 2.2rem); line-height: 1.05; letter-spacing: -.052em; }
.snapshot-card p { margin: 12px 0 0; color: rgba(244,239,228,.66); font-weight: 600; line-height: 1.7; }
.snapshot-kv { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 16px; }
.snapshot-kv div { min-width: 0; padding: 11px; border: 1px solid rgba(244,239,228,.085); border-radius: 16px; background: rgba(0,0,0,.14); }
.snapshot-kv span { display: block; color: rgba(124,230,211,.74); font: 760 .58rem/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }
.snapshot-kv strong { display: block; margin-top: 7px; overflow: hidden; color: rgba(244,239,228,.88); font-size: .95rem; line-height: 1.18; text-overflow: ellipsis; white-space: nowrap; }
.pipeline-track { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 9px; margin-top: 18px; }
.pipeline-step { position: relative; min-height: 172px; padding: 14px; border: 1px solid rgba(244,239,228,.095); border-radius: 20px; background: linear-gradient(145deg, rgba(246,241,228,.05), rgba(0,0,0,.17)); box-shadow: inset 0 1px 0 rgba(255,255,255,.03); }
.pipeline-step:not(:last-child)::after { position: absolute; top: 31px; right: -9px; width: 9px; height: 1px; content: ""; background: linear-gradient(90deg, rgba(232,255,122,.48), transparent); }
.pipeline-step b { display: grid; place-items: center; width: 30px; height: 30px; border-radius: 999px; color: #0b0d10; background: var(--accent); font: 820 .7rem/1 var(--mono); }
.pipeline-step strong { display: block; margin-top: 16px; color: rgba(244,239,228,.93); font-size: 1rem; line-height: 1.15; letter-spacing: -.035em; }
.pipeline-step p { display: -webkit-box; margin: 9px 0 0; overflow: hidden; color: rgba(244,239,228,.58); font-size: .82rem; font-weight: 600; line-height: 1.45; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
.pipeline-step span { display: inline-flex; margin-top: 12px; color: rgba(124,230,211,.72); font: 720 .58rem/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }

.reader-guide { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 14px; }
.reader-card { padding: 20px; border: 1px solid rgba(244,239,228,.105); border-radius: 24px; background: linear-gradient(145deg, rgba(246,241,228,.052), rgba(0,0,0,.16)); }
.reader-card h3 { margin: 0; color: rgba(244,239,228,.94); font-size: clamp(1.3rem, 2vw, 2rem); line-height: 1.08; letter-spacing: -.045em; }
.reader-card p { margin: 10px 0 0; color: rgba(244,239,228,.62); font-weight: 600; line-height: 1.7; }
.reader-card ul { display: grid; gap: 8px; margin: 14px 0 0; padding: 0; list-style: none; }
.reader-card li { padding: 10px 11px; border: 1px solid rgba(244,239,228,.075); border-radius: 15px; background: rgba(0,0,0,.12); color: rgba(244,239,228,.66); font-size: .92rem; line-height: 1.55; }
.reader-card li b { color: rgba(244,239,228,.92); }
.term-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin-top: 14px; }
.term-card { min-height: 128px; padding: 13px; border: 1px solid rgba(244,239,228,.085); border-radius: 17px; background: rgba(0,0,0,.13); }
.term-card strong { display: block; color: rgba(232,255,122,.88); font-size: .98rem; letter-spacing: -.03em; }
.term-card p { margin: 8px 0 0; color: rgba(244,239,228,.58); font-size: .82rem; font-weight: 600; line-height: 1.5; }
.report-nav-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
.report-nav-card { position: relative; display: inline-flex; align-items: center; justify-content: center; min-height: 42px; padding: 10px 12px; overflow: hidden; border: 1px solid rgba(244,239,228,.085); border-radius: 999px; color: rgba(244,239,228,.68); background: linear-gradient(180deg, rgba(244,239,228,.045), rgba(244,239,228,.018)); box-shadow: inset 0 1px 0 rgba(255,255,255,.028); font-size: .9rem; font-weight: 610; line-height: 1; letter-spacing: -.018em; white-space: nowrap; transition: color .2s ease, border-color .2s ease, background .2s ease, transform .2s ease; }
.report-nav-card::before { position: absolute; inset: 0; content: ""; background: radial-gradient(circle at 50% 0%, rgba(232,255,122,.12), transparent 64%); opacity: 0; transition: opacity .2s ease; }
.report-nav-card:hover { transform: translateY(-1px); color: rgba(244,239,228,.95); border-color: rgba(232,255,122,.2); background: linear-gradient(180deg, rgba(232,255,122,.075), rgba(244,239,228,.026)); }
.report-nav-card:hover::before { opacity: 1; }
#report-map { display: grid; grid-template-columns: minmax(260px, .82fr) minmax(500px, 1.18fr); gap: 30px; align-items: end; min-height: 250px; padding: 30px; }
#report-map .section-heading { margin-bottom: 0; }
#report-map .section-heading .eyebrow-label { margin-bottom: 12px; }
#report-map .section-heading h2 { max-width: 520px; font-size: clamp(2.7rem, 5.3vw, 5.8rem); line-height: .9; letter-spacing: -.09em; }
#report-map .section-heading h2 em { display: inline-block; margin-left: .08em; }
#report-map .report-nav-grid { justify-self: stretch; width: 100%; max-width: 660px; margin-left: auto; }
.source-label { display: inline-flex; width: fit-content; padding: 4px 7px; border: 1px solid rgba(124,230,211,.2); border-radius: 999px; color: rgba(124,230,211,.78); background: rgba(124,230,211,.045); font: 720 .66rem/1 var(--mono); letter-spacing: .09em; text-transform: uppercase; }
.back-to-top { position: fixed; right: max(18px, calc((100vw - 1180px) / 2)); bottom: 22px; z-index: 20; display: inline-flex; align-items: center; gap: 8px; min-height: 42px; padding: 9px 12px; border: 1px solid rgba(232,255,122,.18); border-radius: 999px; color: rgba(244,239,228,.9); background: rgba(7,8,12,.72); box-shadow: 0 18px 60px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.045); backdrop-filter: blur(18px) saturate(125%); font-size: .86rem; font-weight: 680; letter-spacing: -.02em; transition: transform .2s ease, border-color .2s ease, background .2s ease; }
.back-to-top::before { content: "↑"; display: grid; place-items: center; width: 22px; height: 22px; border-radius: 999px; color: #0b0d10; background: var(--accent); font: 850 .82rem/1 var(--mono); }
.back-to-top:hover { transform: translateY(-2px); border-color: rgba(232,255,122,.34); background: rgba(14,16,18,.84); }
.source-label { margin-bottom: 12px; }
.source-label[data-source="analysis"] { border-color: rgba(232,255,122,.22); color: rgba(232,255,122,.84); background: rgba(232,255,122,.055); }
.source-label[data-source="review"] { border-color: rgba(255,159,104,.22); color: rgba(255,159,104,.84); background: rgba(255,159,104,.055); }
.source-label[data-source="export"] { border-color: rgba(155,140,255,.24); color: #b9adff; background: rgba(155,140,255,.055); }
.metric-list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin: 0; padding: 0; list-style: none; }
.metric-list li { padding: 14px; border: 1px solid rgba(244,239,228,.095); border-radius: 16px; background: rgba(246,241,228,.032); }
.metric-list span { display: block; color: var(--muted); font: 720 .7rem/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }
.metric-list strong { display: block; margin-top: 10px; color: var(--ink); font-size: 1.45rem; line-height: 1; }

.manual-grid { display: grid; gap: 14px; }
.manual-overview { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(320px, .75fr); gap: 14px; }
.manual-panel { padding: 20px; border: 1px solid rgba(244,239,228,.105); border-radius: 24px; background: radial-gradient(circle at 100% 0%, rgba(124,230,211,.08), transparent 14rem), rgba(0,0,0,.16); }
.manual-panel h3 { margin: 0; color: rgba(244,239,228,.94); font-size: clamp(1.5rem, 2.4vw, 2.5rem); line-height: 1.05; letter-spacing: -.06em; }
.manual-panel p { margin: 12px 0 0; color: rgba(244,239,228,.68); font-weight: 610; line-height: 1.72; }
.manual-pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.manual-pill-row span { padding: 7px 10px; border: 1px solid rgba(124,230,211,.2); border-radius: 999px; color: rgba(124,230,211,.82); background: rgba(124,230,211,.045); font: 760 .66rem/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }
.manual-layer { display: grid; grid-template-columns: 86px minmax(0, 1fr); gap: 14px; padding: 18px; border: 1px solid rgba(244,239,228,.105); border-radius: 24px; background: linear-gradient(145deg, rgba(246,241,228,.052), rgba(0,0,0,.16)); }
.manual-layer-num { display: grid; place-items: center; width: 64px; height: 64px; border: 1px solid rgba(232,255,122,.22); border-radius: 20px; color: var(--accent); background: rgba(232,255,122,.045); font: 820 1rem/1 var(--mono); }
.manual-layer h3 { margin: 0; color: rgba(244,239,228,.94); font-size: clamp(1.25rem, 2vw, 2rem); line-height: 1.05; letter-spacing: -.045em; }
.manual-layer > div > p { margin: 9px 0 0; color: rgba(244,239,228,.66); font-weight: 600; line-height: 1.7; }
.manual-facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: 14px; }
.manual-facts div { min-width: 0; padding: 10px; border: 1px solid rgba(244,239,228,.085); border-radius: 15px; background: rgba(0,0,0,.14); }
.manual-facts span { display: block; color: rgba(124,230,211,.72); font: 760 .58rem/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }
.manual-facts strong { display: block; margin-top: 6px; overflow: hidden; color: rgba(244,239,228,.88); font-size: .92rem; line-height: 1.18; text-overflow: ellipsis; white-space: nowrap; }
.manual-list { display: grid; gap: 8px; margin: 14px 0 0; padding: 0; list-style: none; }
.manual-list li { padding: 10px 12px; border: 1px solid rgba(244,239,228,.08); border-radius: 15px; background: rgba(0,0,0,.12); color: rgba(244,239,228,.62); font-size: .92rem; }
.manual-list b { color: rgba(244,239,228,.9); }
.evidence-table { width: 100%; margin-top: 14px; border-collapse: collapse; overflow: hidden; border-radius: 18px; }
.evidence-table th, .evidence-table td { padding: 12px; border-bottom: 1px solid rgba(244,239,228,.08); text-align: left; vertical-align: top; }
.evidence-table th { color: rgba(124,230,211,.78); font: 780 .66rem/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }
.evidence-table td { color: rgba(244,239,228,.68); font-size: .9rem; }

.workflow-chain { display: grid; gap: 10px; margin: 16px 0 0; padding: 0; list-style: none; counter-reset: workflow; }
.workflow-chain li { position: relative; display: grid; grid-template-columns: 54px minmax(0, 1fr); gap: 10px; padding: 14px; border: 1px solid rgba(244,239,228,.095); border-radius: 18px; background: linear-gradient(145deg, rgba(246,241,228,.045), rgba(0,0,0,.16)); }
.workflow-chain li b { grid-row: span 4; display: grid; place-items: center; width: 42px; height: 42px; border: 1px solid rgba(124,230,211,.22); border-radius: 14px; color: rgba(124,230,211,.9); background: rgba(124,230,211,.05); font: 820 .82rem/1 var(--mono); }
.workflow-chain li strong { color: rgba(244,239,228,.92); font-size: 1.05rem; line-height: 1.2; }
.workflow-chain li p { margin: 0; color: rgba(244,239,228,.66); font-weight: 600; line-height: 1.55; }
.workflow-chain li em, .workflow-chain li span { color: rgba(244,239,228,.46); font: 720 .66rem/1.4 var(--mono); letter-spacing: .04em; font-style: normal; }
@media (max-width: 860px) { .manual-overview, .manual-layer, .manual-facts { grid-template-columns: 1fr; } .manual-layer-num { width: 52px; height: 52px; } }

.asset-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.anchor-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
.anchor-card { position: relative; overflow: hidden; min-height: 190px; padding: 18px; border: 1px solid rgba(244,239,228,.105); border-radius: 24px; background: linear-gradient(145deg, rgba(246,241,228,.06), rgba(0,0,0,.18)); }
.anchor-card::before { content: ""; position: absolute; inset: 0 0 auto; height: 3px; background: linear-gradient(90deg, rgba(232,255,122,.9), rgba(124,230,211,.7), rgba(140,109,255,.58)); opacity: .72; }
.anchor-card h3 { margin: 8px 0 8px; font-size: 1.05rem; line-height: 1.16; letter-spacing: -.03em; }
.anchor-card p { margin: 0; color: rgba(244,239,228,.64); font-weight: 600; line-height: 1.62; }
.anchor-meta { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 14px; }
.anchor-meta span { padding: 6px 8px; border: 1px solid rgba(244,239,228,.1); border-radius: 999px; color: rgba(244,239,228,.68); background: rgba(0,0,0,.14); font: 720 .66rem/1 var(--mono); }
.composition-panel { margin-top: 16px; padding: 18px; border: 1px solid rgba(124,230,211,.16); border-radius: 24px; background: linear-gradient(145deg, rgba(124,230,211,.07), rgba(0,0,0,.18)); }
.export-hub { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.export-link { display: grid; min-height: 130px; align-content: space-between; padding: 16px; border: 1px solid rgba(244,239,228,.11); border-radius: 18px; background: rgba(0,0,0,.16); }
.export-link strong { color: rgba(244,239,228,.9); letter-spacing: -.03em; }
.export-link span { color: var(--muted); font-size: .86rem; }
.pattern-list li strong { font-size: 1.05rem; }

.lang-toggle { display: inline-flex; align-items: center; justify-content: center; min-width: 38px; min-height: 34px; border: 1px solid rgba(244,239,228,.13); border-radius: 999px; color: var(--accent); background: rgba(232,255,122,.055); font: 720 .78rem/1 var(--mono); letter-spacing: .08em; cursor: pointer; }
.lang-toggle:hover { border-color: rgba(232,255,122,.32); background: rgba(232,255,122,.1); }

.eyebrow-label { margin: 0 0 16px; color: var(--accent-2); font-family: var(--mono); font-size: .72rem; font-weight: 760; letter-spacing: .12em; text-transform: uppercase; }
.hero-title-grid { display: grid; gap: clamp(8px, 1.2vw, 16px); max-width: 860px; }
.hero-title-grid .title-word { display: block; width: fit-content; color: transparent; background: var(--title-gradient); background-clip: text; -webkit-background-clip: text; font-size: clamp(4rem, 9vw, 8.4rem); font-weight: 790; line-height: .82; letter-spacing: -.085em; }
.hero-title-grid .title-subject { display: block; color: transparent; background: linear-gradient(110deg, var(--ink) 0%, var(--ink) 48%, rgba(232,255,122,.9) 82%); background-clip: text; -webkit-background-clip: text; font-size: clamp(2.5rem, 5.4vw, 5rem); font-weight: 780; line-height: .95; letter-spacing: -.075em; }
[id] { scroll-margin-top: 132px; }
#reader-guide, #anatomy-snapshot, #method-layer, #workflow-pipeline, #implementation-decoder, #trust-review, #appendix, #manual, #report-map, #manual-composition-detail, #manual-workflow-detail, #manual-resource-detail, #manual-learning-detail, #manual-evidence-table { scroll-margin-top: 142px; }
.manual-layer { scroll-margin-top: 148px; }
.section-heading { display: grid; gap: 10px; margin-bottom: 18px; }
.section-heading h2 { width: fit-content; max-width: 100%; margin: 0; background: linear-gradient(110deg, var(--ink) 0%, var(--ink) 64%, rgba(232,255,122,.7) 100%); background-clip: text; -webkit-background-clip: text; }
.section-heading h2 em { color: var(--accent); font-style: normal; text-shadow: 0 0 22px rgba(232,255,122,.12); }
.section-heading .heading-accent { color: var(--accent); }
.channel-card[data-channel="report"] { --channel-color: var(--accent); }
.channel-card[data-channel="vault"] { --channel-color: var(--accent-2); }
.channel-card[data-channel="data"] { --channel-color: #9b8cff; }
.channel-card[data-channel="graph"] { --channel-color: var(--warn); }

.report-note { display: grid; gap: 7px; max-width: 720px; margin-top: 14px; padding: 14px 16px; border: 1px solid rgba(124,230,211,.18); border-radius: 18px; background: rgba(124,230,211,.045); color: rgba(244,239,228,.64); font-size: .9rem; font-weight: 540; line-height: 1.58; }
.report-note a { width: fit-content; color: rgba(232,255,122,.86); font-weight: 740; letter-spacing: -.01em; }
.report-note[data-run-kind="demo fixture"] { border-color: rgba(255,159,104,.18); background: rgba(255,159,104,.045); }
.report-note[data-run-kind="mock run"] { border-color: rgba(155,140,255,.2); background: rgba(155,140,255,.045); }



/* Report/Repo visual alignment pass. */
.shell { width: min(1240px, calc(100% - 32px)); padding-top: 18px; }
.topbar { margin-bottom: 24px; border-color: rgba(244,239,228,.105); background: rgba(7,8,12,.72); box-shadow: 0 18px 70px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.035); backdrop-filter: blur(22px) saturate(126%); }
.nav a { font-weight: 720; }
.hero, .section { border-color: rgba(244,239,228,.105); background: linear-gradient(145deg, rgba(246,241,228,.062), rgba(246,241,228,.018)); box-shadow: 0 28px 90px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.035); }
.report-hero { min-height: 540px; padding: clamp(24px, 4vw, 46px); background: radial-gradient(circle at 0% 0%, rgba(232,255,122,.11), transparent 22rem), radial-gradient(circle at 100% 18%, rgba(124,230,211,.12), transparent 24rem), linear-gradient(145deg, rgba(246,241,228,.075), rgba(246,241,228,.02)); }
.hero-grid { grid-template-columns: minmax(0, 1fr) 360px; align-items: end; min-height: 450px; }
.report-kicker { border-radius: 999px; min-width: 0; padding: 8px 12px; border-left-color: rgba(124,230,211,.22); background: rgba(124,230,211,.045); }
.report-kicker::before, .report-kicker::after, .report-kicker i { display: none; }
.report-kicker span { color: rgba(124,230,211,.82); font-family: var(--mono); font-size: .68rem; font-weight: 780; letter-spacing: .1em; }
.report-kicker strong { display: none; }
.hero-title-grid { gap: 6px; max-width: 780px; }
.hero-title-grid .title-word { color: rgba(244,239,228,.96); background: none; -webkit-text-fill-color: rgba(244,239,228,.96); font-size: clamp(4rem, 9vw, 8.2rem); text-shadow: none; }
.hero-title-grid .title-subject { width: fit-content; color: transparent; background: linear-gradient(110deg, rgba(244,239,228,.9), rgba(232,255,122,.9) 52%, rgba(124,230,211,.75)); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(2.7rem, 5.2vw, 5rem); text-shadow: none; filter: none; }
.hero-lede { max-width: 760px; color: rgba(244,239,228,.68); font-weight: 560; }
.archive-brief { align-self: end; min-height: 300px; border-radius: 26px; background: radial-gradient(circle at 100% 0%, rgba(124,230,211,.11), transparent 13rem), linear-gradient(145deg, rgba(10,12,12,.86), rgba(4,5,7,.72)); backdrop-filter: blur(24px) saturate(124%); }
.stat, .card, .metric-list li, .export-link { border-color: rgba(244,239,228,.095); background: rgba(0,0,0,.15); }
.export-link { min-height: 142px; border-radius: 20px; transition: transform .22s ease, border-color .22s ease, background .22s ease; }
.export-link:hover { transform: translateY(-3px); border-color: rgba(232,255,122,.24); background: linear-gradient(145deg, rgba(232,255,122,.06), rgba(0,0,0,.16)); }




/* Final report chrome normalization: match the entry page topbar. */
.topbar { width: min(1160px, calc(100% - 32px)); margin-inline: auto; padding: 10px 10px 10px 14px; border: 1px solid var(--line); background: rgba(9,10,15,.72); box-shadow: none; backdrop-filter: blur(22px); }
.brand { color: var(--ink); font: 720 .95rem/1 var(--font); }
.brand-mark { width: 12px; height: 12px; box-shadow: 0 0 28px rgba(232,255,122,.72); }
.nav { gap: 2px; color: var(--muted); font-size: .88rem; }
.nav a { padding: 8px 12px; border: 0; color: var(--muted); font: 720 .88rem/1 var(--font); }
.nav a:hover { color: var(--ink); background: rgba(244,239,228,.08); }

/* Manual section compacting: the ten anatomy layers read as a card grid, not a long wall. */
#manual .manual-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; }
#manual .manual-overview { grid-column: 1 / -1; }
#manual .manual-layer { grid-template-columns: 58px minmax(0, 1fr); padding: 16px; }
#manual .manual-layer-num { width: 48px; height: 48px; border-radius: 16px; font-size: .86rem; }
#manual .manual-layer h3 { font-size: clamp(1.12rem, 1.5vw, 1.46rem); }
#manual .manual-layer > div > p { line-height: 1.52; }
#manual .manual-facts { grid-template-columns: 1fr; gap: 6px; }
#manual .manual-list li { padding: 8px 10px; font-size: .86rem; line-height: 1.48; }
@media (max-width: 980px) { #manual .manual-grid { grid-template-columns: 1fr; } }

/* Report rhythm repair: compact manual navigation, same chrome language as topbar. */
#report-map { display: block; min-height: auto; padding: 24px; }
#report-map .section-heading { margin-bottom: 16px; }
#report-map .section-heading h2 { max-width: none; font-size: clamp(2.1rem, 3.8vw, 3.8rem); line-height: .96; letter-spacing: -.07em; }
#report-map .report-nav-grid { width: 100%; max-width: none; margin: 0; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }
#report-map .report-nav-card { min-height: 38px; padding: 9px 12px; font-size: .84rem; font-weight: 720; }
#exports .channel-grid { margin-bottom: 14px; }
.manual-grid { gap: 14px; }
.manual-layer { min-height: auto; }

@media (max-width: 980px) { .hero-grid, .channel-grid, .asset-grid, .anchor-grid, .export-hub, .snapshot-grid, .reader-guide { grid-template-columns: 1fr 1fr; } .pipeline-track { grid-template-columns: repeat(3, minmax(0, 1fr)); } .term-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } #report-map { grid-template-columns: 1fr; align-items: start; } #report-map .report-nav-grid { justify-self: start; width: 100%; grid-template-columns: repeat(4, minmax(0, 1fr)); } }

@media (max-width: 860px) { .grid, .two-col, .channel-grid, .hero-grid, .asset-grid, .anchor-grid, .export-hub, .metric-list, .snapshot-grid, .pipeline-track, .reader-guide, .term-grid { grid-template-columns: 1fr; } .hero, .section { padding: 22px; } .topbar { align-items: flex-start; border-radius: 22px; flex-direction: column; } #report-map .report-nav-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .report-nav-card { min-width: 0; } .pipeline-step:not(:last-child)::after { display: none; } }
""".strip()


REPORT_JS = """
function setLanguage(language) {
  document.documentElement.lang = language === 'en' ? 'en' : 'zh-CN';
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    const nextText = node.dataset[language];
    if (nextText) node.textContent = nextText;
  });
  document.querySelectorAll('[data-lang-toggle]').forEach((button) => {
    button.textContent = language === 'en' ? '中' : 'EN';
    button.setAttribute('aria-label', language === 'en' ? '切换中文' : 'Switch to English');
  });
  localStorage.setItem('asa-language', language);
}
const savedLanguage = localStorage.getItem('asa-language') || 'zh';
setLanguage(savedLanguage);
document.querySelectorAll('[data-lang-toggle]').forEach((button) => {
  button.addEventListener('click', () => {
    const current = localStorage.getItem('asa-language') || 'zh';
    setLanguage(current === 'en' ? 'zh' : 'en');
  });
});
""".strip()


def export_report(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = _read_optional_json(run_dir / "inventory.json", {})
    quality = _read_optional_json(run_dir / "quality_report.json", None) or quality_report_for_run(run_dir)
    review_summary = _read_optional_json(run_dir / "review_summary.json", None) or summarize_run_reviews(run_dir)
    patterns = _read_optional_json(run_dir / "patterns" / "patterns.json", {"patterns": []})
    anchors = _read_optional_json(output_dir.parent / "anchors" / "anchors.json", {"anchors": []})
    composition_plan = _read_optional_json(output_dir.parent / "anchors" / "composition_plan.json", {})
    skills = _collect_skills(run_dir, inventory, quality, review_summary)

    _copy_artifacts(run_dir, output_dir / "artifacts")
    write_text(output_dir / "assets" / "report.css", REPORT_CSS + "\n")
    write_text(output_dir / "assets" / "report.js", REPORT_JS + "\n")
    write_text(output_dir / "index.html", _render_index(run_dir, output_dir, skills, inventory, quality, review_summary, patterns, anchors, composition_plan))
    _write_cinema_manifest(output_dir, run_dir, skills, inventory, quality, review_summary, patterns)
    skills_output = output_dir / "skills"
    for skill in skills:
        write_text(skills_output / f"{skill['id']}.html", _render_skill_page(run_dir, skill))

    return {
        "run_dir": str(run_dir),
        "output_dir": str(output_dir),
        "skill_count": len(skills),
        "index": str(output_dir / "index.html"),
        "skill_pages": [str(skills_output / f"{skill['id']}.html") for skill in skills],
    }


def _write_cinema_manifest(output_dir: Path, run_dir: Path, skills: list[dict[str, Any]], inventory: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any], patterns: dict[str, Any]) -> None:
    cinema_dir = output_dir.parent / "cinema"
    run_meta = _read_optional_json(run_dir / "run.json", {})
    workflow_step_count = sum(len(skill.get("workflow", {}).get("workflow_steps", [])) for skill in skills)
    script_count = sum(len(skill.get("package", {}).get("scripts", [])) for skill in skills)
    reference_count = sum(len(skill.get("package", {}).get("references", [])) for skill in skills)
    asset_count = sum(len(skill.get("package", {}).get("assets", [])) for skill in skills)
    file_count = sum(len(source.get("files", [])) for source in inventory.get("source_inventories", [])) or inventory.get("repository", {}).get("total_files_scanned", 0)
    approved = sum(1 for skill in review_summary.get("skills", []) if skill.get("approved_for_publish"))
    top_patterns = patterns.get("patterns", [])[:3]
    skill_preview = [_cinema_skill_preview(skill) for skill in skills[:6]]
    quality_cards = _cinema_quality_cards(review_summary)
    resource_nodes = _cinema_resource_nodes(skills)
    repo_profile = _cinema_repo_profile(run_dir, inventory, run_meta, skills, file_count, quality, review_summary, approved)
    skill_focuses = [_cinema_skill_focus(skill) for skill in skills]
    skill_focus = skill_focuses[0] if skill_focuses else None
    repo_overview_cards = [
        {
            "title": "Skills",
            "subtitle": f"{len(skills)} detected",
            "body": _join_preview([item["name"] for item in skill_preview], "No skills"),
            "facts": [
                {"label": "skills", "value": str(len(skills))},
                {"label": "approved", "value": str(approved)},
                {"label": "revision", "value": str(review_summary.get("status_counts", {}).get("needs_revision", 0))},
            ],
            "tags": [f"{approved} approved", f"{review_summary.get('status_counts', {}).get('needs_revision', 0)} revision", "inventory"],
            "href": "../report/#skills",
        },
        {
            "title": "Workflow",
            "subtitle": f"{workflow_step_count} steps",
            "body": "Action paths, fallback signals, and future condition nodes.",
            "facts": [
                {"label": "steps", "value": str(workflow_step_count)},
                {"label": "source", "value": "workflow analysis"},
                {"label": "next", "value": "conditions / fallbacks"},
            ],
            "tags": [f"{workflow_step_count} steps", "trace", "audit"],
            "href": "../report/#workflow",
        },
        {
            "title": "Resources",
            "subtitle": f"{script_count + reference_count + asset_count} assets",
            "body": f"Scripts {script_count}, references {reference_count}, assets {asset_count}.",
            "facts": [
                {"label": "scripts", "value": str(script_count)},
                {"label": "refs", "value": str(reference_count)},
                {"label": "assets", "value": str(asset_count)},
            ],
            "tags": [f"{script_count} scripts", f"{reference_count} refs", f"{asset_count} assets"],
            "href": "../report/#resources",
        },
        {
            "title": "Quality",
            "subtitle": f"{review_summary.get('totals', {}).get('issues', 0)} review issues",
            "body": _join_preview([card["body"] for card in quality_cards], "No reviewer issues"),
            "facts": [
                {"label": "rules", "value": str(quality.get("issue_count", 0))},
                {"label": "review", "value": str(review_summary.get("totals", {}).get("issues", 0))},
                {"label": "status", "value": "rules passed" if quality.get("publishable_by_rules") else "needs review"},
            ],
            "tags": [f"{quality.get('issue_count', 0)} rules", f"{review_summary.get('totals', {}).get('issues', 0)} review", "grounded"],
            "href": "../report/#quality",
        },
        {
            "title": "Patterns",
            "subtitle": f"{len(patterns.get('patterns', []))} candidates",
            "body": _join_preview([pattern.get("zh_name") or pattern.get("canonical_name") or pattern.get("id") for pattern in top_patterns], "No patterns"),
            "facts": [
                {"label": "patterns", "value": str(len(patterns.get("patterns", [])))},
                {"label": "top", "value": _join_preview([pattern.get("zh_name") or pattern.get("canonical_name") for pattern in top_patterns[:1]], "—")},
                {"label": "mode", "value": "reuse candidates"},
            ],
            "tags": ["reuse", "template", f"{len(patterns.get('patterns', []))} patterns"],
            "href": "../report/#patterns",
        },
        {
            "title": "Model",
            "subtitle": str(run_meta.get("provider", "unknown")),
            "body": f"Provider {run_meta.get('provider', 'unknown')} · language {run_meta.get('language', 'unknown')} · status {run_meta.get('status', 'unknown')}.",
            "facts": [
                {"label": "provider", "value": str(run_meta.get("provider", "unknown"))},
                {"label": "language", "value": str(run_meta.get("language", "unknown"))},
                {"label": "status", "value": str(run_meta.get("status", "unknown"))},
            ],
            "tags": [str(run_meta.get("provider", "unknown")), str(run_meta.get("language", "unknown")), str(run_meta.get("status", "unknown"))],
            "href": "../report/#models",
        },
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_dir.name,
        "report_href": "../report/",
        "repo_href": "../repo/",
        "repo_profile": repo_profile,
        "summary": {
            "skills": len(skills),
            "files": file_count,
            "scripts": script_count,
            "references": reference_count,
            "assets": asset_count,
            "workflow_steps": workflow_step_count,
            "quality_issues": quality.get("issue_count", 0),
            "review_issues": review_summary.get("totals", {}).get("issues", 0),
            "patterns": len(patterns.get("patterns", [])),
            "approved": approved,
            "status": "rules_passed" if quality.get("publishable_by_rules") else "needs_review",
        },
        "model": {
            "provider": run_meta.get("provider", "unknown"),
            "language": run_meta.get("language", "unknown"),
            "status": run_meta.get("status", "unknown"),
            "created_at": run_meta.get("created_at"),
            "completed_at": run_meta.get("completed_at"),
        },
        "skill_preview": skill_preview,
        "top_patterns": top_patterns,
        "quality_cards": quality_cards,
        "resource_nodes": resource_nodes,
        "skill_focus": skill_focus,
        "skill_focuses": skill_focuses,
        "repo_overview_cards": repo_overview_cards,
        "repo_cards": skill_focus.get("cards", repo_overview_cards) if skill_focus else repo_overview_cards,
        "stages": [
            {"key": "source", "title": "Repo Signal", "card_title": "Source", "text": f"本次 run 读取 {file_count or '—'} 个文件，检测到 {len(skills)} 个 skill package。", "input": "GitHub URL / Local path", "action": "collect inventory and detect skill packages", "output": f"{len(skills)} skill(s), {file_count or 0} file(s)", "tags": [f"{file_count or 0} files", f"{len(skills)} skills", "inventory"], "links": [{"label": "Skill 清单", "href": "../report/#skills"}, {"label": "覆盖率", "href": "../report/#coverage"}]},
            {"key": "core", "title": "Skill Core", "card_title": "Core", "text": f"结构分析已生成 {len(skills)} 个 skill 档案，用于呈现 identity、activation、boundary 与 outputs。", "input": "SKILL.md / package layout", "action": "structure analysis", "output": "skill detail pages", "tags": ["identity", "boundary", f"{approved} approved"], "links": [{"label": "Skill 详情", "href": "../report/#skills"}]},
            {"key": "resources", "title": "Resource Split", "card_title": "Resources", "text": f"资源层识别 scripts={script_count}、references={reference_count}、assets={asset_count}。", "input": "scripts / references / assets", "action": "classify resources and dependencies", "output": "resource map", "tags": [f"{script_count} scripts", f"{reference_count} refs", f"{asset_count} assets"], "links": [{"label": "资源依赖", "href": "../report/#resources"}]},
            {"key": "workflow", "title": "Workflow Trace", "card_title": "Workflow", "text": f"工作流层当前包含 {workflow_step_count} 个 step，后续会扩展 action、condition、fallback 与 stop 节点。", "input": "workflow signals / LLM analysis", "action": "reconstruct workflow", "output": f"{workflow_step_count} workflow step(s)", "tags": [f"{workflow_step_count} steps", "actions", "fallbacks"], "links": [{"label": "Workflow", "href": "../report/#workflow"}]},
            {"key": "evidence", "title": "Evidence Lock", "card_title": "Evidence", "text": f"质量层发现 {quality.get('issue_count', 0)} 个确定性问题，Reviewer 汇总 {review_summary.get('totals', {}).get('issues', 0)} 个问题。", "input": "evidence / reviewer outputs", "action": "quality and grounding review", "output": "review cards", "tags": [f"{quality.get('issue_count', 0)} rule issues", f"{review_summary.get('totals', {}).get('issues', 0)} review", "grounding"], "links": [{"label": "质量证据", "href": "../report/#quality"}, {"label": "Reviewer", "href": "../report/#reviews"}]},
            {"key": "report", "title": "Report Release", "card_title": "Report", "text": "拆解结果汇总为 Web Report，并继续分发到 Obsidian、Graph 与 JSON/Data 出口。", "input": "reviewed artifacts", "action": "publish report surfaces", "output": "Web / Obsidian / Graph / JSON", "tags": ["web", "obsidian", "json"], "links": [{"label": "打开报告", "href": "../report/"}, {"label": "输出中心", "href": "../report/#exports"}]},
        ],
    }
    write_json(cinema_dir / "cinema-data.json", manifest)



def _text_value(value: Any, language: str = "zh") -> str:
    if isinstance(value, dict):
        return str(value.get(language) or value.get("en") or value.get("zh") or value.get("name") or value.get("id") or "")
    if value is None:
        return ""
    return str(value)


def _path_value(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("path") or value.get("name") or value.get("id") or "")
    if value is None:
        return ""
    return str(value)


def _detail_items(values: list[Any], fallback: str, *, label: str = "item", limit: int = 5) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for index, value in enumerate(values[:limit], start=1):
        if isinstance(value, dict):
            title = _text_value(value.get("name") or value.get("title") or value.get("question") or value.get("path") or value.get("id"))
            body = _text_value(value.get("action") or value.get("purpose") or value.get("description") or value.get("rationale") or value.get("severity") or value.get("step_type"))
            tone = _text_value(value.get("step_type") or value.get("severity") or value.get("confidence") or label)
        else:
            title = _text_value(value)
            body = ""
            tone = label
        if title or body:
            items.append({"label": f"{label} {index}", "title": title or body, "body": body, "tone": tone})
    if not items:
        items.append({"label": "empty", "title": fallback, "body": "", "tone": "missing"})
    return items

def _cinema_skill_focus(skill: dict[str, Any]) -> dict[str, Any]:
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    review = skill.get("review", {})
    package = skill.get("package", {})
    summary = structure.get("summary", {})
    explicit_triggers = structure.get("trigger_conditions", {}).get("explicit", [])
    inferred_triggers = structure.get("trigger_conditions", {}).get("inferred", [])
    tools = structure.get("tools", [])
    risks = structure.get("risks", [])
    steps = workflow.get("workflow_steps", [])
    reusable = workflow.get("reusable_candidates", [])
    issues = review.get("issues", [])
    scripts = package.get("scripts", [])
    references = package.get("references", [])
    assets = package.get("assets", [])
    skill_href = f"../report/skills/{skill.get('id')}.html"
    return {
        "id": skill.get("id"),
        "name": skill.get("name"),
        "summary": summary.get("zh") or summary.get("en") or "No summary.",
        "status": review.get("status", "unknown"),
        "href": skill_href,
        "cards": [
            {
                "title": "Trigger",
                "subtitle": f"{len(explicit_triggers) + len(inferred_triggers)} signals",
                "body": _join_preview(explicit_triggers + inferred_triggers, "No trigger signals extracted"),
                "facts": [
                    {"label": "explicit", "value": str(len(explicit_triggers))},
                    {"label": "inferred", "value": str(len(inferred_triggers))},
                    {"label": "source", "value": package.get("skill_md_path") or "SKILL.md"},
                ],
                "tags": ["activation", "signals", "skill.md"],
                "href": skill_href,
                "details": _detail_items(explicit_triggers + inferred_triggers, "No trigger signals extracted", label="signal"),
            },
            {
                "title": "Boundary",
                "subtitle": structure.get("skill_type", {}).get("primary", "unknown"),
                "body": structure.get("context_strategy", {}).get("summary") or "Boundary and context strategy are not yet grounded.",
                "facts": [
                    {"label": "agent", "value": _join_preview(structure.get("target_agents", []), "unknown")},
                    {"label": "type", "value": structure.get("skill_type", {}).get("primary", "unknown")},
                    {"label": "confidence", "value": structure.get("confidence", {}).get("overall", "unknown")},
                ],
                "tags": ["scope", "context", "confidence"],
                "href": skill_href,
                "details": _detail_items([*(structure.get("target_agents", []) or []), structure.get("context_strategy", {}).get("progressive_disclosure"), structure.get("context_strategy", {}).get("summary")], "No boundary notes extracted", label="scope"),
            },
            {
                "title": "Tools",
                "subtitle": f"{len(tools)} tools",
                "body": _join_preview([tool.get("name") if isinstance(tool, dict) else tool for tool in tools], "No tools extracted"),
                "facts": [
                    {"label": "tools", "value": str(len(tools))},
                    {"label": "scripts", "value": str(len(scripts))},
                    {"label": "risks", "value": str(len(risks))},
                ],
                "tags": ["tools", "scripts", "risk"],
                "href": skill_href,
                "details": _detail_items([*tools, *scripts, *risks], "No tools or script dependencies extracted", label="tool"),
            },
            {
                "title": "Workflow",
                "subtitle": f"{len(steps)} steps",
                "body": _join_preview([_text_value(step.get("name") if isinstance(step, dict) else step) or (_text_value(step.get("id")) if isinstance(step, dict) else "") for step in steps], _text_value(workflow.get("workflow_summary", {})) or "No workflow steps"),
                "facts": [
                    {"label": "steps", "value": str(len(steps))},
                    {"label": "decisions", "value": str(len(workflow.get("decision_points", [])))},
                    {"label": "failures", "value": str(len(workflow.get("failure_modes", [])))},
                ],
                "tags": ["steps", "decision", "handoff"],
                "href": skill_href,
                "details": _detail_items(steps, "No workflow steps extracted", label="step", limit=6),
            },
            {
                "title": "Evidence",
                "subtitle": review.get("status", "unknown"),
                "body": _join_preview([_text_value(issue.get("description") if isinstance(issue, dict) else issue) for issue in issues], "No review issues"),
                "facts": [
                    {"label": "issues", "value": str(len(issues))},
                    {"label": "missing", "value": str(len(review.get("missing_evidence", [])))},
                    {"label": "approved", "value": str(bool(review.get("approved_for_publish", {}).get("value"))).lower()},
                ],
                "tags": ["evidence", "review", review.get("status", "unknown")],
                "href": "../report/#reviews",
                "details": _detail_items([*issues, *(review.get("missing_evidence", []) or []), *(review.get("unsupported_claims", []) or [])], "No reviewer issues found", label="review"),
            },
            {
                "title": "Reuse",
                "subtitle": f"{len(reusable)} candidates",
                "body": _join_preview(reusable, "Reuse candidates need real analyst output"),
                "facts": [
                    {"label": "reuse", "value": str(len(reusable))},
                    {"label": "refs", "value": str(len(references))},
                    {"label": "assets", "value": str(len(assets))},
                ],
                "tags": ["reuse", "templates", "assets"],
                "href": "../report/#patterns",
                "details": _detail_items([*reusable, *references, *assets], "No reusable assets extracted", label="asset"),
            },
        ],
    }


def _cinema_repo_profile(run_dir: Path, inventory: dict[str, Any], run_meta: dict[str, Any], skills: list[dict[str, Any]], file_count: int, quality: dict[str, Any], review_summary: dict[str, Any], approved: int) -> dict[str, Any]:
    source = inventory.get("source", {})
    repository = inventory.get("repository", {})
    source_type = source.get("type") or "local"
    focused_package = skills[0].get("package", {}) if skills else {}
    focused_source_name = focused_package.get("source_name")
    source_name = focused_source_name or source.get("name") or repository.get("root_path") or run_dir.name
    source_url = source.get("url")
    root_path = repository.get("root_path")
    readme_path = repository.get("readme_path")
    license_path = repository.get("license_path") or source.get("license")
    resolved_commit = source.get("resolved_commit")
    ref = source.get("ref")
    display_name = _repo_display_name(source_name, source_url, root_path)
    primary_skill = skills[0].get("name") if skills else None
    source_label = "GitHub URL" if source_url else ("multi-source" if source_type == "multi" else "local source")
    run_kind = _cinema_run_kind(run_dir, run_meta)
    return {
        "name": display_name,
        "run_kind": run_kind,
        "run_notice": _cinema_run_notice(run_kind),
        "source_label": source_label,
        "source_type": source_type,
        "source_name": source_name,
        "url": source_url,
        "root_path": root_path,
        "readme_path": readme_path,
        "license_path": license_path,
        "resolved_commit": resolved_commit,
        "ref": ref,
        "primary_skill": primary_skill,
        "run_id": run_dir.name,
        "provider": run_meta.get("provider", "unknown"),
        "language": run_meta.get("language", "unknown"),
        "status": run_meta.get("status", "unknown"),
        "facts": [
            {"label": "run", "value": run_dir.name},
            {"label": "source", "value": source_label},
            {"label": "skill", "value": primary_skill or "—"},
            {"label": "readme", "value": readme_path or "—"},
            {"label": "license", "value": license_path or "—"},
            {"label": "commit", "value": (resolved_commit or ref or "—")},
            {"label": "model", "value": str(run_meta.get("provider", "unknown"))},
            {"label": "status", "value": str(run_meta.get("status", "unknown"))},
        ],
        "outputs": [
            {"label": "Formal Repo", "href": "../repo/", "kind": "repo"},
            {"label": "Web Report", "href": "../report/", "kind": "report"},
            {"label": "Artifacts", "href": "../report/artifacts/", "kind": "data"},
            {"label": "Obsidian", "href": "../vault/Open%20in%20Obsidian.html", "kind": "vault"},
            {"label": "Surfaces", "href": "../index.html#surfaces", "kind": "hub"},
        ],
        "trust": [
            {"label": "facts", "value": str(file_count or 0), "tone": "fact"},
            {"label": "rules", "value": str(quality.get("issue_count", 0)), "tone": "pass" if quality.get("issue_count", 0) == 0 else "warn"},
            {"label": "review", "value": str(review_summary.get("totals", {}).get("issues", 0)), "tone": "pass" if review_summary.get("totals", {}).get("issues", 0) == 0 else "warn"},
            {"label": "approved", "value": str(approved), "tone": "fact" if approved else "neutral"},
        ],
    }


def _cinema_run_kind(run_dir: Path, run_meta: dict[str, Any]) -> str:
    if run_dir.name.startswith("demo-"):
        return "demo fixture"
    if run_meta.get("provider") == "mock":
        return "mock run"
    return "real run"


def _cinema_run_notice(run_kind: str) -> str:
    if run_kind == "demo fixture":
        return "Demo fixture for UI preview; not a real model analysis."
    if run_kind == "mock run":
        return "Mock-provider output; use real analyst models before relying on conclusions."
    return "Real run exported from canonical JSON artifacts."


def _repo_display_name(source_name: str, source_url: str | None, root_path: str | None) -> str:
    if source_url:
        clean = source_url.rstrip("/")
        return clean.removesuffix(".git").split("/")[-1] or clean
    if source_name and source_name != "aggregate":
        return source_name
    if root_path:
        return Path(root_path).name
    return source_name or "Skill Repository"


def _cinema_skill_preview(skill: dict[str, Any]) -> dict[str, Any]:
    review = skill.get("review", {})
    summary = skill.get("structure", {}).get("summary", {})
    return {
        "id": skill.get("id"),
        "name": skill.get("name"),
        "status": review.get("status", "unknown"),
        "summary": summary.get("zh") or summary.get("en") or "No summary.",
        "href": f"../report/skills/{skill.get('id')}.html",
    }


def _cinema_quality_cards(review_summary: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for item in review_summary.get("skills", [])[:6]:
        cards.append({
            "title": item.get("skill_id", "skill"),
            "severity": "review",
            "body": f"status={item.get('status', 'unknown')}, issues={item.get('issue_count', 0)}",
            "href": "../report/#reviews",
        })
    return cards


def _cinema_resource_nodes(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for skill in skills:
        package = skill.get("package", {})
        for kind in ("scripts", "references", "assets"):
            for file_ref in package.get(kind, [])[:4]:
                path = file_ref.get("path") if isinstance(file_ref, dict) else str(file_ref)
                nodes.append({"kind": kind[:-1], "path": path, "skill_id": skill.get("id")})
    return nodes[:12]


def _join_preview(values: list[Any], fallback: str) -> str:
    clean = [_preview_value(value) for value in values if value]
    clean = [value for value in clean if value]
    if not clean:
        return fallback
    return " · ".join(clean[:3])


def _preview_value(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("name", "zh", "en", "path", "id", "type"):
            item = value.get(key)
            if item:
                return str(item)
        return ""
    return str(value)


def _collect_skills(run_dir: Path, inventory: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any]) -> list[dict[str, Any]]:
    packages = {item.get("id"): item for item in inventory.get("skill_packages", [])}
    review_by_skill = {item.get("skill_id"): item for item in review_summary.get("skills", [])}
    quality_counts = {item.get("skill_id"): item.get("issue_count", 0) for item in quality.get("skills", [])}
    skills_dir = run_dir / "skills"
    skills: list[dict[str, Any]] = []
    for skill_dir in sorted(path for path in skills_dir.glob("*") if path.is_dir()) if skills_dir.exists() else []:
        skill_id = skill_dir.name
        package = packages.get(skill_id, {})
        structure = _read_optional_json(skill_dir / "structure_analysis.json", {})
        workflow = _read_optional_json(skill_dir / "workflow_analysis.json", {})
        review = _read_optional_json(skill_dir / "review_report.json", {})
        skills.append({
            "id": skill_id,
            "name": package.get("name") or structure.get("skill_id") or skill_id,
            "package": package,
            "structure": structure,
            "workflow": workflow,
            "review": review,
            "review_summary": review_by_skill.get(skill_id, {}),
            "quality_issue_count": quality_counts.get(skill_id, 0),
            "dir": skill_dir,
        })
    return skills


def _report_run_notice_zh(run_kind: str) -> str:
    if run_kind == "demo fixture":
        return "演示夹具仅用于界面预览，不代表真实模型分析结果。"
    if run_kind == "mock run":
        return "Mock 运行用于流程自检，结论不可视为真实模型判断。"
    return "真实运行结果：事实来自确定性 artifacts，模型分析作为第二层解释。"


def _render_index(run_dir: Path, output_dir: Path, skills: list[dict[str, Any]], inventory: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any], patterns: dict[str, Any], anchors: dict[str, Any], composition_plan: dict[str, Any]) -> str:
    approved = sum(1 for skill in review_summary.get("skills", []) if skill.get("approved_for_publish"))
    source_count = len(inventory.get("source_inventories", [])) or len({skill.get("package", {}).get("source_name") for skill in skills if skill.get("package")})
    file_count = sum(len(source.get("files", [])) for source in inventory.get("source_inventories", []))
    script_count = sum(len(skill.get("package", {}).get("scripts", [])) for skill in skills)
    reference_count = sum(len(skill.get("package", {}).get("references", [])) for skill in skills)
    asset_count = sum(len(skill.get("package", {}).get("assets", [])) for skill in skills)
    workflow_step_count = sum(len(skill.get("workflow", {}).get("workflow_steps", [])) for skill in skills)
    review_issue_count = sum(len(skill.get("review", {}).get("issues", [])) for skill in skills)
    run_meta = _read_optional_json(run_dir / "run.json", {})
    run_kind = _cinema_run_kind(run_dir, run_meta)
    run_notice_en = _cinema_run_notice(run_kind)
    run_notice_zh = _report_run_notice_zh(run_kind)
    gate_zh = "规则通过" if quality.get("publishable_by_rules") else "需要复核"
    gate_en = "Rules passed" if quality.get("publishable_by_rules") else "Needs review"
    gate_class = "ok" if quality.get("publishable_by_rules") else "bad"
    body = f"""
    <section class="hero report-hero">
      <div class="hero-grid">
        <div>
          <div class="report-kicker"><span>{i18n('Skill 拆解档案', 'Skill Anatomy Archive')}</span><strong>Agent Skill Anatomy</strong><i aria-hidden="true"></i></div>
          <h1 class="hero-title-grid" aria-label="Skill 拆解档案"><span class="title-word">Skill</span><span class="title-subject">{i18n('拆解档案', 'Anatomy Archive')}</span></h1>
          <p class="hero-lede">{i18n('这是一份可分享的研究作品：汇总 Skill 结构、workflow、证据、review 与候选模式，并链接回首页选择不同输出格式。', 'A shareable research artifact: Skill structure, workflows, evidence, review, and pattern candidates, with the home UI owning surface selection.')}</p>
          <div class="run-meta"><div class="meta-item"><span class="meta-label">{i18n('运行', 'Run')}</span><code class="meta-value mono">{escape(run_dir.name)}</code></div><div class="meta-item"><span class="meta-label">{i18n('类型', 'Kind')}</span><strong class="run-kind-chip" data-run-kind="{escape(run_kind)}">{escape(run_kind)}</strong></div><div class="meta-item"><span class="meta-label">{i18n('状态', 'Status')}</span><strong class="meta-value {gate_class}">{i18n(gate_zh, gate_en)}</strong></div></div>
          <div class="report-note" data-run-kind="{escape(run_kind)}"><span>{i18n(run_notice_zh, run_notice_en)}</span><a href="../repo/">{i18n('打开正式 Repo 档案', 'Open formal Repo dossier')}</a><a href="../index.html#surfaces">{i18n('返回首页选择输出格式', 'Back to surface selector')}</a></div>
        </div>
        <div class="archive-brief">
          <span class="eyebrow-label">{i18n('档案摘要', 'Archive Summary')}</span>
          <ul>
            <li><span>{i18n('结构', 'Structure')}</span><strong>{len(skills)} Skills</strong></li>
            <li><span>{i18n('证据', 'Evidence')}</span><strong>{quality.get('issue_count', 0)} {i18n('个问题', 'issue(s)')}</strong></li>
            <li><span>{i18n('状态', 'Status')}</span><strong class="{gate_class}">{i18n(gate_zh, gate_en)}</strong></li>
            <li><span>{i18n('复用', 'Reuse')}</span><strong>{len(patterns.get('patterns', []))} Patterns</strong></li>
          </ul>
          <p class="micro-copy">{i18n(f"{approved} 个 skill 已批准；确定性质量状态仅作为元信息展示。", f"{approved} approved skill(s); deterministic quality state is shown as metadata only.")}</p>
        </div>
      </div>
      <div class="grid">{_stat('Skills', 'Skills', len(skills))}{_stat('来源', 'Sources', source_count)}{_stat('质量问题', 'Quality issues', quality.get('issue_count', 0))}{_stat('模式', 'Patterns', len(patterns.get('patterns', [])))}</div>
    </section>
    {_reader_guide(skills)}
    <section class="section" id="report-map">{_section_heading('阅读路径', 'Reading Path', '说明书', 'Manual', '主线', 'path')}<div class="report-nav-grid">{_nav_card('guide', '导览', 'Guide', '#reader-guide')}{_nav_card('snapshot', '快照', 'Snapshot', '#anatomy-snapshot')}{_nav_card('manual', '说明书', 'Manual', '#manual')}{_nav_card('composition', '组成', 'Composition', '#manual-composition-detail')}{_nav_card('workflow', '串联', 'Workflow', '#manual-workflow-detail')}{_nav_card('decoder', '实现', 'Implementation', '#implementation-decoder')}{_nav_card('evidence', '证据', 'Evidence', '#manual-evidence-table')}{_nav_card('reuse', '复用', 'Reuse', '#manual-learning-detail')}{_nav_card('method', '方法', 'Method', '#method-layer')}{_nav_card('anchors', '锚点', 'Anchors', '#anchors')}{_nav_card('outputs', '出口', 'Outputs', '#exports')}</div></section>
    {_anatomy_snapshot(skills, patterns)}
    {_manual_report(skills, inventory, quality, review_summary, patterns)}
    {_manual_composition_matrix(skills[0]) if skills else ''}
    {_manual_workflow_chain(skills[0]) if skills else ''}
    {_workflow_pipeline(skills)}
    {_implementation_decoder(skills)}
    <section class="section" id="trust-review">{_section_heading('可信度', 'Trust Review', '证据', 'Evidence', '与质量', 'and Quality')}<span class="source-label" data-source="review">review</span><div class="two-col"><div class="card feature-card"><h3>{i18n('规则门禁', 'Rule Gate')}</h3><p>{i18n('规则层面可发布' if quality.get('publishable_by_rules') else '需要质量复核', 'Publishable by rules' if quality.get('publishable_by_rules') else 'Needs quality review')}</p></div><div class="card feature-card"><h3>{i18n('Reviewer 问题', 'Reviewer Issues')}</h3><p>{review_issue_count}</p></div></div>{_evidence_audit_panel(skills[0]) if skills else ''}</section>
    <section class="section" id="manual-evidence-table">{_section_heading('证据对照', 'Evidence Map', '结论', 'Claims', '回到原文', 'to Source')}{_manual_evidence_table(skills[0]) if skills else ''}</section>
    {_manual_learning_assets(skills[0], patterns) if skills else ''}
    {_method_layer_summary(skills, patterns)}
    {_anchor_surface(anchors, composition_plan)}
    <section class="section" id="patterns">{_section_heading('模型提炼', 'Pattern Miner', '候选', 'Pattern', '模式', 'candidates')}<span class="source-label" data-source="analysis">analysis</span><ul class="list pattern-list">{''.join(_pattern_item(pattern) for pattern in patterns.get('patterns', [])) or f'<li>{i18n("暂无模式。", "No patterns found.")}</li>'}</ul></section>
    <section class="section" id="exports">{_section_heading('输出中心', 'Export Hub', '可视化', 'Output', '入口', 'hub')}<span class="source-label" data-source="export">export</span><div class="channel-grid">{_output_channels(output_dir)}</div><div class="export-hub"><a class="export-link" href="../repo/"><strong>Formal Repo</strong><span>Review-ready dossier</span></a><a class="export-link" href="../cinema/"><strong>Demo</strong><span>First-run visual story</span></a><a class="export-link" href="./artifacts/"><strong>Artifacts</strong><span>JSON source of truth</span></a><a class="export-link" href="../vault/Open%20in%20Obsidian.html"><strong>Obsidian</strong><span>Learning vault</span></a><a class="export-link" href="../data/"><strong>Data</strong><span>JSONL CSV manifest</span></a><a class="export-link" href="../graph/"><strong>Graph</strong><span>Relation map</span></a></div></section>
    <section class="section" id="appendix">{_section_heading('附录', 'Appendix', '原始', 'Raw', '数据', 'data')}<div class="report-nav-grid">{_nav_card('facts', '确定性事实', 'Facts', '#coverage')}{_nav_card('skills', 'Skill 清单', 'Skills', '#skills')}{_nav_card('quality', '质量门禁', 'Quality', '#quality')}{_nav_card('reviews', '审查汇总', 'Reviews', '#reviews')}{_nav_card('models', '模型产出', 'Models', '#models')}{_nav_card('artifacts', 'Artifacts', 'Artifacts', './artifacts/')}</div></section>
    <section class="section" id="coverage">{_section_heading('确定性事实', 'Deterministic Facts', '拆解', 'Decomposition', '覆盖率', 'coverage')}<span class="source-label" data-source="deterministic">deterministic</span><ul class="metric-list"><li><span>{i18n('文件', 'Files')}</span><strong>{file_count or '—'}</strong></li><li><span>{i18n('Skills', 'Skills')}</span><strong>{len(skills)}</strong></li><li><span>Scripts</span><strong>{script_count}</strong></li><li><span>References</span><strong>{reference_count}</strong></li><li><span>Assets</span><strong>{asset_count}</strong></li><li><span>Issues</span><strong>{quality.get('issue_count', 0)}</strong></li></ul></section>
    <section class="section" id="skills">{_section_heading('已分析技能', 'Analyzed Skills', 'Skill', 'Skill', '清单', 'inventory')}<span class="source-label" data-source="analysis">analysis</span><table class="table"><thead><tr><th>{i18n('技能', 'Skill')}</th><th>{i18n('状态', 'Status')}</th><th>{i18n('质量', 'Quality')}</th><th>{i18n('产物', 'Artifacts')}</th></tr></thead><tbody>{''.join(_skill_row(skill) for skill in skills)}</tbody></table></section>
    <section class="section" id="quality">{_section_heading('规则质量', 'Rule Quality', '质量', 'Quality', '门禁', 'gate')}<span class="source-label" data-source="review">review</span><div class="two-col"><div class="card feature-card"><h3>{i18n('规则门禁', 'Rule Gate')}</h3><p>{i18n('规则层面可发布' if quality.get('publishable_by_rules') else '需要质量复核', 'Publishable by rules' if quality.get('publishable_by_rules') else 'Needs quality review')}</p></div><div class="card feature-card"><h3>{i18n('严重程度统计', 'Severity Counts')}</h3><p class="mono">{escape(_format_counts(quality.get('severity_counts', {})))}</p></div></div>{_issues_table(quality.get('issues', []))}</section>
    <section class="section" id="reviews">{_section_heading('审查层', 'Reviewer Layer', 'Reviewer', 'Reviewer', '汇总', 'summary')}<span class="source-label" data-source="review">review</span><div class="two-col"><div class="card feature-card"><h3>{i18n('状态统计', 'Status Counts')}</h3><p class="mono">{escape(_format_counts(review_summary.get('status_counts', {})))}</p></div><div class="card feature-card"><h3>{i18n('问题总计', 'Totals')}</h3><p class="mono">{escape(_format_counts(review_summary.get('totals', {})))}</p></div></div></section>
    <section class="section" id="models">{_section_heading('模型分析', 'Model Analysis', '模型', 'Model', '产出', 'outputs')}<span class="source-label" data-source="analysis">analysis</span><div class="two-col"><div class="card feature-card"><h3>{i18n('当前模式', 'Current Mode')}</h3><p>{i18n('当前报告展示单次 run 的模型分析结果；模型对比仅作为开发测试与校准产物，不作为用户侧入口。', 'This report shows one run; model comparison remains a development and calibration artifact, not a user-facing entry.')}</p></div><div class="card feature-card"><h3>{i18n('Reviewer 问题', 'Reviewer Issues')}</h3><p>{review_issue_count}</p></div></div></section>
    """
    return _page("Agent Skill Anatomy Report", body, "index")


def _render_skill_page(run_dir: Path, skill: dict[str, Any]) -> str:
    structure = skill["structure"]
    workflow = skill["workflow"]
    review = skill["review"]
    summary = structure.get("summary", {})
    workflow_summary = workflow.get("workflow_summary", {})
    steps = workflow.get("workflow_steps", [])
    body = f"""
    <section class="hero"><p class="label">{i18n("技能详情", "Skill Detail")}</p><h1>{escape(skill['name'])}</h1><p class="muted">{escape(summary.get('zh') or summary.get('en') or 'No summary.')}</p><div class="grid">{_stat('工作流步骤', 'Workflow steps', len(steps))}{_stat('质量问题', 'Quality issues', skill.get('quality_issue_count', 0))}{_stat('审查状态', 'Review status', review.get('status', 'unknown'))}{_stat('置信度', 'Confidence', structure.get('confidence', {}).get('overall', 'unknown'))}</div></section>
    <section class="section"><h2>{i18n("结构", "Structure")}</h2><div class="two-col"><div class="card"><h3>ZH</h3><p>{escape(summary.get('zh') or '—')}</p></div><div class="card"><h3>EN</h3><p>{escape(summary.get('en') or '—')}</p></div></div><ul class="list"><li><span class="pill">Target agents</span> {escape(_join_preview(structure.get('target_agents', []), 'unknown'))}</li><li><span class="pill">Skill type</span> {escape(structure.get('skill_type', {}).get('primary', 'unknown'))}</li><li><span class="pill">Skill file</span> <code>{escape(skill.get('package', {}).get('skill_md_path') or structure.get('source', {}).get('skill_md_path') or 'unknown')}</code></li></ul></section>
    <section class="section"><h2>{i18n("工作流", "Workflow")}</h2><p class="muted">{escape(workflow_summary.get('zh') or workflow_summary.get('en') or 'No workflow summary.')}</p><ul class="list">{''.join(_step_item(step) for step in steps) or f'<li>{i18n("暂无工作流步骤。", "No workflow steps.")}</li>'}</ul></section>
    <section class="section"><h2>{i18n("审查", "Review")}</h2><div class="two-col"><div class="card"><h3>{i18n("是否批准", "Approved")}</h3><p>{i18n('是', 'Yes') if review.get('approved_for_publish', {}).get('value') else i18n('否', 'No')}</p></div><div class="card"><h3>{i18n("理由", "Rationale")}</h3><p>{escape(review.get('approved_for_publish', {}).get('rationale', '—'))}</p></div></div><ul class="list">{''.join(_review_issue(issue) for issue in review.get('issues', [])) or f'<li>{i18n("暂无 reviewer 问题。", "No reviewer issues.")}</li>'}</ul></section>
    <section class="section"><h2>{i18n("原始 Artifacts", "Canonical Artifacts")}</h2><ul class="list">{_artifact_link(run_dir, skill['dir'] / 'structure_analysis.json')}{_artifact_link(run_dir, skill['dir'] / 'workflow_analysis.json')}{_artifact_link(run_dir, skill['dir'] / 'review_report.json')}{_artifact_link(run_dir, skill['dir'] / 'source_snapshot.json')}</ul></section>
    """
    return _page(f"{skill['name']} - Agent Skill Anatomy", body, "skill")

def _reader_guide(skills: list[dict[str, Any]]) -> str:
    skill_name = skills[0].get("name", "Skill") if skills else "Skill"
    terms = [
        ("Skill", "可以理解为给 Agent 使用的一组任务说明、资源和边界。"),
        ("Trigger", "什么时候应该调用这个 skill，例如用户请求生成艺术代码。"),
        ("Workflow", "Agent 从理解需求到交付结果的步骤链。"),
        ("Evidence", "报告里的结论能回到 SKILL.md、模板文件或 reviewer 判断。"),
    ]
    term_html = ''.join(f'<article class="term-card"><strong>{escape(name)}</strong><p>{escape(desc)}</p></article>' for name, desc in terms)
    newcomer = f"把 {skill_name} 当成一个可复用的 Agent 行为模块来看：它规定什么时候调用、读取哪些资源、按什么步骤执行、最后产出什么。"
    newcomer_en = f"Treat {skill_name} as a reusable agent behavior module: when to invoke it, what resources to read, what steps to follow, and what to deliver."
    return f"""<section class="section" id="reader-guide">{_section_heading('读者导览', 'Reader Guide', '不懂 Skill', 'New To Skills', '也能读', 'Start Here')}<div class="reader-guide"><article class="reader-card"><h3>{i18n('如果你不熟悉 Skill', 'If You Are New To Skills')}</h3><p>{i18n(newcomer, newcomer_en)}</p><ul><li><b>{i18n('先看快照', 'Start with snapshot')}</b> · {i18n('理解这个 skill 的用途、输入、输出和状态。', 'Understand purpose, inputs, outputs, and status.')}</li><li><b>{i18n('再看链路', 'Then read pipeline')}</b> · {i18n('理解它如何一步步完成任务。', 'Understand how it completes the task step by step.')}</li><li><b>{i18n('最后看复用', 'Finish with reuse')}</b> · {i18n('判断哪些模式能迁移到你自己的 skill。', 'Decide what can transfer into your own skill.')}</li></ul></article><article class="reader-card"><h3>{i18n('如果你熟悉 Skill 设计', 'If You Design Skills')}</h3><p>{i18n('重点看触发边界、上下文加载、资源职责、证据扎根和复用资产。这些部分决定一个 skill 是否可维护、可迁移、可评估。', 'Focus on activation boundaries, context loading, resource roles, evidence grounding, and reusable assets. These determine maintainability, transferability, and evaluability.')}</p><div class="term-grid">{term_html}</div></article></div></section>"""

def _method_layer_summary(skills: list[dict[str, Any]], patterns: dict[str, Any]) -> str:
    if not skills:
        return ""
    skill = skills[0]
    structure = skill.get("structure", {}) or {}
    workflow = skill.get("workflow", {}) or {}
    review = skill.get("review", {}) or {}
    identity = structure.get("identity", {}) or {}
    activation = structure.get("activation", {}) or {}
    resource_roles = structure.get("resource_roles", []) or []
    workflow_trace = workflow.get("workflow_trace", {}) or {}
    evidence_audit = review.get("evidence_audit", {}) or {}
    reuse_assets = patterns.get("reuse_assets", {}) or {}

    identity_text = _text_value(identity.get("one_line", {})) or _text_value(structure.get("summary", {})) or "—"
    trigger_text = _join_preview(activation.get("explicit_triggers", []) or structure.get("trigger_conditions", {}).get("explicit", []) or [], "未发现显式触发")
    resource_text = _join_preview([item.get("path") for item in resource_roles if isinstance(item, dict)], skill.get("package", {}).get("skill_md_path") or "SKILL.md")
    trace_text = _join_preview(workflow_trace.get("pipeline", []) or [step.get("step_type") for step in workflow.get("workflow_steps", []) if isinstance(step, dict)], "detect → inspect → deliver")
    audit_text = evidence_audit.get("rationale") or _join_preview(review.get("missing_evidence", []) or [], "等待 reviewer 证据审计")
    reuse_text = _join_preview(reuse_assets.get("checklists", []) or reuse_assets.get("patterns", []) or [pattern.get("zh_name") or pattern.get("canonical_name") for pattern in patterns.get("patterns", []) or []], "从 workflow 与资源角色中提炼")

    cards = [
        ("01", "身份", "Identity", "它是什么", "What it is", identity_text),
        ("02", "触发", "Activation", "什么时候该用", "When to use", trigger_text),
        ("03", "资源", "Resources", "读哪些文件", "What to read", resource_text),
        ("04", "链路", "Trace", "如何串联", "How it connects", trace_text),
        ("05", "证据", "Evidence", "是否可信", "Can it be trusted", audit_text),
        ("06", "复用", "Reuse", "学走什么", "What to reuse", reuse_text),
    ]
    card_html = "".join(
        f'<article class="manual-layer"><span class="manual-layer-num">{num}</span><div><p class="eyebrow-label">{i18n(label_zh, label_en)}</p><h3>{i18n(title_zh, title_en)}</h3><p>{escape(str(detail))}</p></div></article>'
        for num, label_zh, label_en, title_zh, title_en, detail in cards
    )
    return f'''<section class="section" id="method-layer">{_section_heading('方法层', 'Method Layer', '拆解', 'Anatomy', '如何发生', 'method')}<p class="muted">{i18n('这里把内置 meta-skills 的拆解视角显式展示出来：先确认身份，再判断触发边界，随后解释资源、链路、证据和复用。', 'This exposes the built-in meta-skill viewpoints: identity first, then activation boundaries, resources, trace, evidence, and reuse.')}</p><div class="manual-stack">{card_html}</div></section>'''


def _anchor_surface(anchors_doc: dict[str, Any], composition_plan: dict[str, Any]) -> str:
    anchors = anchors_doc.get("anchors", []) if isinstance(anchors_doc, dict) else []
    if not anchors and not composition_plan:
        return ""
    type_counts: dict[str, int] = {}
    for anchor in anchors:
        if isinstance(anchor, dict):
            anchor_type = str(anchor.get("anchor_type") or "unknown")
            type_counts[anchor_type] = type_counts.get(anchor_type, 0) + 1
    top_anchors = [anchor for anchor in anchors if isinstance(anchor, dict)][:6]
    cards = "".join(_anchor_card(anchor) for anchor in top_anchors)
    if not cards:
        cards = f'<article class="anchor-card"><h3>{i18n("暂无锚点", "No anchors yet")}</h3><p>{i18n("运行 export-letuen 或 export-anchors 后会在这里显示可复用锚点。", "Run export-letuen or export-anchors to show reusable anchors here.")}</p></article>'
    counts_html = "".join(f'<span>{escape(key)} · {value}</span>' for key, value in sorted(type_counts.items()))
    if not counts_html:
        counts_html = f'<span>{i18n("等待导出", "waiting for export")}</span>'
    composition_html = _composition_plan_panel(composition_plan)
    heading = _section_heading("复用锚点", "Reusable Anchors", "拆小", "Split", "再拼接", "Compose")
    description = i18n("这里展示可以被借用、组合或固化的 LetUen anchors。默认只做 sidecar 输出，不修改用户已有 skill。", "This shows LetUen anchors that can be borrowed, composed, or solidified. By default they are sidecar outputs and do not modify existing user skills.")
    return f'<section class="section" id="anchors">{heading}<span class="source-label" data-source="export">anchors</span><p class="muted">{description}</p><div class="manual-pill-row">{counts_html}</div><div class="anchor-grid">{cards}</div>{composition_html}<p class="muted"><a class="pill" href="../anchors/anchors.json">anchors.json</a> <a class="pill" href="../anchors/composition_plan.json">composition_plan.json</a></p></section>'


def _anchor_card(anchor: dict[str, Any]) -> str:
    name = anchor.get("name") if isinstance(anchor.get("name"), dict) else {}
    summary = anchor.get("summary") if isinstance(anchor.get("summary"), dict) else {}
    anchor_type = str(anchor.get("anchor_type") or "unknown")
    confidence = str(anchor.get("confidence") or _anchor_evidence_confidence(anchor))
    risk = anchor.get("risk") if isinstance(anchor.get("risk"), dict) else {}
    risk_score = str(risk.get("score") or "unknown")
    reuse_modes = anchor.get("reuse_modes") if isinstance(anchor.get("reuse_modes"), list) else []
    reuse = _join_preview(reuse_modes, "reference_only")
    title = escape(_text_value(name) or anchor.get("id", "anchor"))
    body = escape(_text_value(summary) or anchor.get("id", ""))
    return f'<article class="anchor-card"><span class="pill">{escape(anchor_type)}</span><h3>{title}</h3><p>{body}</p><div class="anchor-meta"><span>confidence={escape(confidence)}</span><span>risk={escape(risk_score)}</span><span>{escape(reuse)}</span></div></article>'


def _anchor_evidence_confidence(anchor: dict[str, Any]) -> str:
    evidence = anchor.get("source_evidence") or anchor.get("evidence") or []
    for item in evidence:
        if isinstance(item, dict) and item.get("confidence"):
            return str(item.get("confidence"))
    return "unknown"


def _composition_plan_panel(plan: dict[str, Any]) -> str:
    if not plan:
        title = i18n("组合计划", "Composition Plan")
        body = i18n("未提供 composition request，因此本次只展示 anchors。传入 --composition-request 后会生成可组合方案。", "No composition request was provided, so this report only shows anchors. Pass --composition-request to generate a composition plan.")
        return f'<div class="composition-panel"><h3>{title}</h3><p>{body}</p></div>'
    selected = plan.get("selected_anchors") if isinstance(plan.get("selected_anchors"), list) else []
    rejected = plan.get("rejected_anchors") if isinstance(plan.get("rejected_anchors"), list) else []
    dispatch = plan.get("dispatch_policy") if isinstance(plan.get("dispatch_policy"), dict) else {}
    solidification = plan.get("solidification") if isinstance(plan.get("solidification"), dict) else {}
    title = i18n("组合计划", "Composition Plan")
    body = escape(_text_value(plan.get("summary", {})) or plan.get("composition_form", "composition"))
    return f'<div class="composition-panel"><h3>{title}</h3><p>{body}</p><div class="manual-pill-row"><span>{escape(str(plan.get("composition_form", "unknown")))}</span><span>{len(selected)} selected</span><span>{len(rejected)} rejected</span><span>{escape(str(dispatch.get("policy", "prefer_existing_skill")))}</span><span>solidify={escape(str(solidification.get("requested", False)).lower())}</span></div></div>'
def _anatomy_snapshot(skills: list[dict[str, Any]], patterns: dict[str, Any]) -> str:
    if not skills:
        return ""
    skill = skills[0]
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    package = skill.get("package", {})
    review = skill.get("review", {})
    anatomy = structure.get("file_anatomy", {}) or {}
    pattern_name = _join_preview([item.get("zh_name") or item.get("canonical_name") for item in patterns.get("patterns", []) or []], "Concept → Template → Artifact")
    kv = [
        ("type", structure.get("skill_type", {}).get("primary", "unknown")),
        ("pattern", pattern_name),
        ("inputs", _join_preview(structure.get("inputs", []) or [], "unknown")),
        ("outputs", _join_preview(structure.get("outputs", []) or [], "unknown")),
        ("resources", _join_preview([_path_value(item) for item in (package.get("related_files", []) or [])[:3]], package.get("skill_md_path") or "SKILL.md")),
        ("status", review.get("status", "unknown")),
    ]
    kv_html = ''.join(f'<div><span>{escape(label)}</span><strong>{escape(value)}</strong></div>' for label, value in kv)
    role = _join_preview([_path_value(item) for item in anatomy.get("templates", []) or []], "模板和资源将在执行阶段按需读取")
    return f"""<section class="section" id="anatomy-snapshot">{_section_heading('拆解快照', 'Anatomy Snapshot', '先看', 'Read The', '结论', 'Summary')}<div class="snapshot-grid"><article class="snapshot-card"><h3>{escape(skill.get('name', 'Skill'))}</h3><p>{escape(_text_value(structure.get('summary', {})))}</p><div class="snapshot-kv">{kv_html}</div></article><article class="snapshot-card"><h3>{i18n('核心组成', 'Core Composition')}</h3><p>{escape(role)}</p><div class="manual-pill-row"><span>{escape(package.get('skill_md_path') or 'SKILL.md')}</span><span>{len(workflow.get('workflow_steps', []) or [])} steps</span><span>{len(patterns.get('patterns', []) or [])} patterns</span></div></article></div></section>"""


def _implementation_decoder(skills: list[dict[str, Any]]) -> str:
    if not skills:
        return ""
    skill = skills[0]
    structure = skill.get("structure", {})
    package = skill.get("package", {})
    workflow = skill.get("workflow", {})
    rows = [
        ("Trigger", "判断是否该用", _join_preview(structure.get("trigger_conditions", {}).get("explicit", []) or [], "从描述中识别任务意图"), package.get("skill_md_path") or "SKILL.md"),
        ("Context", "决定读什么", _text_value(structure.get("context_strategy", {}).get("description")) or "按需读取主指令和模板", package.get("skill_md_path") or "SKILL.md"),
        ("Resource", "提供稳定骨架", _join_preview([_path_value(item) for item in package.get("related_files", []) or []], "相关模板/资源"), "templates / related files"),
        ("Workflow", "把意图转成产物", _text_value(workflow.get("workflow_summary", {})), "workflow_analysis.json"),
        ("Quality", "检查能否发布", skill.get("review", {}).get("status", "unknown"), "review_report.json"),
    ]
    body = ''.join(f'<tr><td>{escape(layer)}</td><td>{escape(job)}</td><td>{escape(detail)}</td><td><code>{escape(source)}</code></td></tr>' for layer, job, detail, source in rows)
    return f"""<section class="section" id="implementation-decoder">{_section_heading('实现对照', 'Implementation Decoder', '设计如何', 'How Design', '落到文件', 'Maps To Files')}<p class="muted">{i18n('给熟悉 skill 设计的读者：这里把报告结论映射回触发、上下文、资源、workflow 和质量产物。', 'For skill designers: this maps report claims back to activation, context, resources, workflow, and quality artifacts.')}</p><table class="evidence-table"><thead><tr><th>Layer</th><th>Job</th><th>Decoded Detail</th><th>Source</th></tr></thead><tbody>{body}</tbody></table></section>"""

def _workflow_pipeline(skills: list[dict[str, Any]]) -> str:
    if not skills:
        return ""
    skill = skills[0]
    workflow = skill.get("workflow", {})
    steps = [step for step in workflow.get("workflow_steps", []) or [] if isinstance(step, dict)]
    selected = _pipeline_select_steps(steps)
    if not selected:
        return ""
    cards = []
    for index, step in enumerate(selected, 1):
        cards.append(
            '<article class="pipeline-step">'
            f'<b>{index:02d}</b>'
            f'<strong>{escape(_text_value(step.get("name", {})) or step.get("id", "step"))}</strong>'
            f'<p>{escape(_text_value(step.get("action", {})) or step.get("step_type", ""))}</p>'
            f'<span>{escape(step.get("step_type", "step"))} · {escape(step.get("confidence", "unknown"))}</span>'
            '</article>'
        )
    return f"""<section class="section" id="workflow-pipeline">{_section_heading('执行链路', 'Workflow Pipeline', '如何', 'How It', '串联实现', 'Connects')}<p class="muted">{escape(_text_value(workflow.get('workflow_summary', {})))}</p><div class="pipeline-track">{''.join(cards)}</div></section>"""


def _pipeline_select_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(steps) <= 6:
        return steps
    indexes = [0, 1, max(2, len(steps) // 3), max(3, len(steps) // 2), max(4, len(steps) - 2), len(steps) - 1]
    selected: list[dict[str, Any]] = []
    seen: set[int] = set()
    for index in indexes:
        if 0 <= index < len(steps) and index not in seen:
            selected.append(steps[index])
            seen.add(index)
    return selected[:6]

def _manual_report(skills: list[dict[str, Any]], inventory: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any], patterns: dict[str, Any]) -> str:
    if not skills:
        return f'<section class="section" id="manual"><p>{i18n("暂无 skill 可拆解。", "No skill available for anatomy.")}</p></section>'
    skill = skills[0]
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    review = skill.get("review", {})
    package = skill.get("package", {})
    summary = _text_value(structure.get("summary", {})) or "暂无摘要"
    workflow_summary = _text_value(workflow.get("workflow_summary", {})) or "暂无 workflow 摘要"
    skill_type = structure.get("skill_type", {}).get("primary", "unknown")
    confidence = structure.get("confidence", {}).get("overall", "unknown")
    explicit_triggers = structure.get("trigger_conditions", {}).get("explicit", []) or []
    inferred_triggers = structure.get("trigger_conditions", {}).get("inferred", []) or []
    inputs = structure.get("inputs", []) or []
    outputs = structure.get("outputs", []) or []
    risks = structure.get("risks", []) or []
    steps = workflow.get("workflow_steps", []) or []
    reusable = workflow.get("reusable_candidates", []) or []
    scripts = package.get("scripts", []) or []
    references = package.get("references", []) or []
    assets = package.get("assets", []) or []
    related_files = package.get("related_files", []) or []
    review_issues = review.get("issues", []) or []
    approved = bool(review.get("approved_for_publish", {}).get("value"))
    pattern_items = patterns.get("patterns", []) or []
    resources = [*scripts, *references, *assets, *related_files]
    layer_specs = [
        ("01", "身份层", "Identity Layer", "确认它到底是什么：类型、目标、价值、最终产物。", "Identify what this skill is: type, target, value, and final outputs.", [("type", skill_type), ("confidence", confidence), ("skill file", package.get("skill_md_path") or "SKILL.md")], [_label_item("摘要", summary), _label_item("目标 Agent", _join_preview(structure.get("target_agents", []) or [], "unknown")), _label_item("最终产物", _join_preview(outputs, "未明确"))], "manual-identity"),
        ("02", "触发层", "Activation Layer", "说明什么时候应该调用，什么时候不应该调用。", "Explain when to invoke it and when not to.", [("explicit", len(explicit_triggers)), ("inferred", len(inferred_triggers)), ("source", package.get("skill_md_path") or "SKILL.md")], [_label_item("显式触发", _join_preview(explicit_triggers, "无显式触发")), _label_item("语义触发", _join_preview(inferred_triggers, "无推断触发")), _label_item("边界提示", _text_value(structure.get("context_strategy", {}).get("summary")) or "未明确")], "manual-activation"),
        ("03", "输入层", "Input Layer", "拆出运行前需要的用户意图、文件、配置和默认假设。", "Extract user intent, files, configuration, and assumptions needed before execution.", [("inputs", len(inputs)), ("outputs", len(outputs)), ("risks", len(risks))], [_label_item("必需输入", _join_preview(inputs, "未明确")), _label_item("输出目标", _join_preview(outputs, "未明确")), _label_item("缺失风险", _join_preview(risks, "暂无风险"))], "manual-input"),
        ("04", "资源层", "Resource Layer", "解释 SKILL.md、模板、脚本、引用和资产分别承担什么职责。", "Explain the responsibilities of SKILL.md, templates, scripts, references, and assets.", [("scripts", len(scripts)), ("references", len(references)), ("assets/files", len(assets) + len(related_files))], [_label_item("脚本", _join_preview([_path_value(x) for x in scripts], "无脚本")), _label_item("引用", _join_preview([_path_value(x) for x in references], "无引用")), _label_item("相关文件", _join_preview([_path_value(x) for x in related_files[:6]], "无相关文件"))], "manual-resources"),
        ("05", "上下文层", "Context Layer", "说明哪些内容应该优先读，哪些内容按需加载，避免上下文污染。", "Describe priority reading, on-demand loading, and context-noise control.", [("strategy", _text_value(structure.get("context_strategy", {}).get("progressive_disclosure")) or "unknown"), ("files", len(resources)), ("confidence", confidence)], [_label_item("上下文策略", _text_value(structure.get("context_strategy", {}).get("summary")) or "未明确"), _label_item("优先文件", package.get("skill_md_path") or "SKILL.md"), _label_item("按需文件", _join_preview([_path_value(x) for x in related_files[:4]], "未明确"))], "manual-context"),
        ("06", "执行层", "Workflow Layer", "把用户意图如何一步步变成最终产物讲清楚。", "Show how user intent becomes the final deliverable step by step.", [("steps", len(steps)), ("decisions", len(workflow.get("decision_points", []) or [])), ("failures", len(workflow.get("failure_modes", []) or []))], [_label_item("流程摘要", workflow_summary), *[_step_summary(step) for step in steps[:6]]], "manual-workflow"),
        ("07", "控制层", "Control Layer", "拆出约束、禁止行为、质量门槛和停止条件。", "Extract constraints, prohibitions, quality gates, and stop conditions.", [("verify", len(workflow.get("verification_points", []) or [])), ("warnings", len(workflow.get("warnings", []) or [])), ("review", review.get("status", "unknown"))], [_label_item("验证点", _join_preview(workflow.get("verification_points", []) or [], "未明确")), _label_item("失败模式", _join_preview(workflow.get("failure_modes", []) or [], "未明确")), _label_item("Reviewer", _join_preview(review_issues, "暂无 reviewer 问题"))], "manual-control"),
        ("08", "产出层", "Output Layer", "说明它会产出哪些主产物、中间产物、学习产物和复用产物。", "Describe primary, intermediate, learning, and reusable outputs.", [("declared", len(outputs)), ("vault", "ready"), ("json", "ready")], [_label_item("声明产出", _join_preview(outputs, "未明确")), _label_item("报告产出", "Web Report / Demo / Obsidian Vault / JSON Artifacts"), _label_item("中间产物", "structure_analysis.json / workflow_analysis.json / review_report.json")], "manual-output"),
        ("09", "证据层", "Evidence Layer", "每个关键判断要能回到原文、文件结构或明确推断。", "Every key claim should map back to source text, file structure, or explicit inference.", [("quality issues", skill.get("quality_issue_count", 0)), ("review issues", len(review_issues)), ("approved", str(approved).lower())], [_label_item("证据状态", "通过" if approved else "需要复核"), _label_item("缺失证据", _join_preview(review.get("missing_evidence", []) or [], "未发现")), _label_item("不支持结论", _join_preview(review.get("unsupported_claims", []) or [], "未发现"))], "manual-evidence"),
        ("10", "复用层", "Reuse Layer", "把这个 skill 沉淀成模式、模板、清单和改写建议。", "Turn this skill into patterns, templates, checklists, and rewrite ideas.", [("candidates", len(reusable)), ("patterns", len(pattern_items)), ("assets", len(assets) + len(related_files))], [_label_item("复用候选", _join_preview(reusable, "暂无复用候选")), _label_item("模式提炼", _join_preview([p.get("zh_name") or p.get("canonical_name") for p in pattern_items], "暂无模式")), _label_item("迁移建议", _manual_reuse_advice(skill_type, reusable, pattern_items))], "manual-reuse"),
    ]
    layers = "".join(_manual_layer(*spec) for spec in layer_specs)
    return f"""
    <section class="section" id="manual">
      {_section_heading('拆解说明书', 'Anatomy Manual', '先看懂', 'Understand', '这个 Skill', 'the Skill')}
      <div class="manual-grid">
        <div class="manual-overview">
          <div class="manual-panel"><h3>{escape(skill.get('name', 'Skill'))}</h3><p>{escape(summary)}</p><div class="manual-pill-row"><span>{escape(skill_type)}</span><span>{len(steps)} workflow steps</span><span>{escape(review.get('status', 'unknown'))}</span><span>{len(pattern_items)} pattern(s)</span></div></div>
          <div class="manual-panel"><h3>{i18n('一句话拆解', 'One-line Anatomy')}</h3><p>{escape(_manual_one_liner(skill, workflow_summary))}</p></div>
        </div>
        {layers}
      </div>
    </section>
    """

def _manual_composition_matrix(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    package = skill.get("package", {})
    anatomy = structure.get("file_anatomy", {}) or {}
    rows = [
        ("SKILL.md", package.get("skill_md_path") or anatomy.get("main_skill_file") or "SKILL.md", "主指令、触发描述、两阶段流程和质量约束", "必读"),
        ("frontmatter", structure.get("frontmatter", {}).get("name") or skill.get("name"), "名称、描述、license 等入口元数据", "入口"),
        ("templates", _join_preview([_path_value(item) for item in anatomy.get("templates", [])], "未识别模板"), "固定输出骨架，降低生成不确定性", "高复用"),
        ("related files", _join_preview([_path_value(item) for item in package.get("related_files", [])], "无相关文件"), "与 skill 同包的模板、license 或辅助文件", "按需读取"),
        ("outputs", _join_preview(structure.get("outputs", []) or [], "未声明"), "最终交付给用户的文件或内容", "交付"),
    ]
    matrix_body = ''.join(f'<tr><td>{escape(kind)}</td><td>{escape(path)}</td><td>{escape(role)}</td><td>{escape(mode)}</td></tr>' for kind, path, role, mode in rows)
    resources: list[dict[str, Any]] = []
    for role in structure.get("resource_roles", []) or []:
        if isinstance(role, dict):
            resources.append(role)
    if not resources:
        for template in anatomy.get("templates", []) or []:
            if isinstance(template, dict):
                resources.append({"type": "template", "path": template.get("path", "template"), "role": template.get("role", "固定模板"), "stage": "生成/包装阶段", "read_policy": "on_demand", "reuse_value": "high"})
        for item in package.get("related_files", []) or []:
            if isinstance(item, dict):
                resources.append({"type": item.get("file_type", "file"), "path": item.get("path", "file"), "role": item.get("reason", "same skill package"), "stage": "按需读取", "read_policy": "on_demand", "reuse_value": "medium"})
    if not resources:
        resources.append({"type": "skill", "path": package.get("skill_md_path") or "SKILL.md", "role": "主指令与流程说明", "stage": "inspect", "read_policy": "must_read", "reuse_value": "medium"})
    resource_body = ''.join(
        f'<tr><td>{escape(item.get("type", "resource"))}</td><td><code>{escape(item.get("path", "file"))}</code></td><td>{escape(item.get("role", "—"))}</td><td>{escape(item.get("stage", "—"))}</td><td>{escape(item.get("read_policy", "unknown"))}</td><td>{escape(item.get("reuse_value", "unknown"))}</td></tr>'
        for item in resources[:12]
    )
    return f"""<section class="section" id="manual-composition-detail">{_section_heading('组成与资源', 'Composition And Resources', '组成', 'Composition', '职责', 'roles')}<div class="two-col"><div><h3>{i18n('组成矩阵', 'Composition Matrix')}</h3><table class="evidence-table"><thead><tr><th>Part</th><th>Source</th><th>Responsibility</th><th>Use</th></tr></thead><tbody>{matrix_body}</tbody></table></div><div><h3>{i18n('资源职责', 'Resource Roles')}</h3><table class="evidence-table"><thead><tr><th>Type</th><th>Path</th><th>Responsibility</th><th>Stage</th><th>Read</th><th>Reuse</th></tr></thead><tbody>{resource_body}</tbody></table></div></div></section>"""


def _manual_workflow_chain(skill: dict[str, Any]) -> str:
    workflow = skill.get("workflow", {}) or {}
    trace = workflow.get("workflow_trace", {}) or {}
    trace_steps = [step for step in trace.get("steps", []) or [] if isinstance(step, dict)]
    steps = trace_steps or workflow.get("workflow_steps", []) or []
    if not steps:
        return f'''<section class="section" id="manual-workflow-detail">{_section_heading('完整链路', 'Full Workflow', '如何', 'How It', '串联', 'Connects')}<p class="muted">{i18n('暂无 workflow step。', 'No workflow steps.')}</p></section>'''
    cards = []
    for index, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            cards.append(f'<li><b>{index:02d}</b><strong>{escape(step)}</strong></li>')
            continue
        evidence = step.get("evidence", []) or []
        evidence_text = ""
        if evidence and isinstance(evidence[0], dict):
            evidence_text = f'{evidence[0].get("source_path", "source")} · {evidence[0].get("evidence_type", "evidence")}';
        name = _text_value(step.get("name", {})) or step.get("id", "step")
        action = _text_value(step.get("action", {})) or str(step.get("action") or step.get("step_type", ""))
        resources = _join_preview(step.get("resources", []) or [], "no resource mapped")
        downstream = _join_preview(step.get("downstream", []) or [], "no downstream declared")
        cards.append('<li>' + f'<b>{index:02d}</b>' + f'<strong>{escape(name)}</strong>' + f'<p>{escape(action)}</p>' + f'<em>{escape(step.get("actor", "unknown"))} · confidence={escape(step.get("confidence", "unknown"))}</em>' + f'<span>{escape(resources)} → {escape(downstream)}</span>' + f'<span>{escape(evidence_text or "no direct evidence attached")}</span>' + '</li>')
    failure_modes = trace.get("failure_modes", []) or workflow.get("failure_modes", []) or []
    failure_html = ""
    if failure_modes:
        failure_html = '<div class="card"><h3>' + i18n('失败模式', 'Failure Modes') + '</h3><ul class="manual-list">' + ''.join(f'<li>{escape(_text_value(item) or item)}</li>' for item in failure_modes[:6]) + '</ul></div>'
    pipeline = _join_preview(trace.get("pipeline", []) or [], "")
    pipeline_html = f'<p class="muted mono">{escape(pipeline)}</p>' if pipeline else ""
    return f'''<section class="section" id="manual-workflow-detail">{_section_heading('完整链路', 'Full Workflow', '如何', 'How It', '串联', 'Connects')}{pipeline_html}<ol class="workflow-chain">{''.join(cards)}</ol>{failure_html}</section>'''


def _manual_resource_roles(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    anatomy = structure.get("file_anatomy", {}) or {}
    package = skill.get("package", {})
    resources: list[tuple[str, str, str, str]] = []
    for template in anatomy.get("templates", []) or []:
        if isinstance(template, dict):
            resources.append(("template", template.get("path", "template"), template.get("role", "固定模板"), "生成/包装阶段"))
    for item in package.get("related_files", []) or []:
        if isinstance(item, dict):
            resources.append((item.get("file_type", "file"), item.get("path", "file"), item.get("reason", "same skill package"), "按需读取"))
    if not resources:
        resources.append(("skill", package.get("skill_md_path") or "SKILL.md", "主指令与流程说明", "必读"))
    rows = ''.join(f'<tr><td>{escape(kind)}</td><td><code>{escape(path)}</code></td><td>{escape(role)}</td><td>{escape(stage)}</td></tr>' for kind, path, role, stage in resources[:12])
    return f'''<section class="section" id="manual-resource-detail">{_section_heading('资源职责', 'Resource Roles', '每个文件', 'Each File', '负责什么', 'Does What')}<table class="evidence-table"><thead><tr><th>Type</th><th>Path</th><th>Responsibility</th><th>Stage</th></tr></thead><tbody>{rows}</tbody></table></section>'''


def _manual_learning_assets(skill: dict[str, Any], patterns: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    pattern_items = patterns.get("patterns", []) or []
    reuse_assets = patterns.get("reuse_assets", {}) or {}
    pattern_name = _join_preview([item.get("zh_name") or item.get("canonical_name") for item in pattern_items], "Concept-first Template-driven Generation")
    fallback_checklist = [
        "先识别触发条件，不要把所有创作请求都归入该 skill。",
        "先生成概念/哲学中间产物，再进入代码或模板实现。",
        "模板负责稳定结构，模型负责填充算法与参数。",
        "每个 workflow step 都要能回到 SKILL.md 或文件结构证据。",
        "复用时优先迁移两阶段链路，而不是直接复制具体艺术风格。",
    ]
    notes = [
        _label_item("可学习模式", pattern_name),
        _label_item("适用场景", "创意代码、可视化、报告生成、模板化网页产物"),
        _label_item("迁移方式", "把 Concept → Template → Artifact 的顺序抽成新 skill 骨架"),
        _label_item("注意风险", _join_preview(structure.get("risks", []) or [], "暂无风险")),
        _label_item("复用候选", _join_preview(workflow.get("reusable_candidates", []) or [], "从 workflow 与模板中提炼")),
    ]
    asset_specs = [
        ("patterns", "可迁移模式", "Reusable Patterns", reuse_assets.get("patterns", []) or [pattern_name]),
        ("templates", "模板骨架", "Templates", reuse_assets.get("templates", []) or []),
        ("checklists", "复用检查清单", "Reuse Checklist", reuse_assets.get("checklists", []) or fallback_checklist),
        ("anti_patterns", "反模式", "Anti-Patterns", reuse_assets.get("anti_patterns", []) or []),
        ("extension_ideas", "扩展建议", "Extension Ideas", reuse_assets.get("extension_ideas", []) or []),
    ]
    cards = []
    for key, title_zh, title_en, values in asset_specs:
        items = values if isinstance(values, list) else [values]
        item_html = ''.join(f'<li>{escape(_text_value(item) or item)}</li>' for item in items[:8]) or f'<li>{i18n("暂无", "None yet")}</li>'
        cards.append(f'<article class="card" data-reuse-asset="{escape(key)}"><h3>{i18n(title_zh, title_en)}</h3><ul class="manual-list">{item_html}</ul></article>')
    return f'''<section class="section" id="manual-learning-detail">{_section_heading('学习复用', 'Learning Assets', '如何', 'How To', '学走它', 'Reuse It')}<div class="two-col"><div class="card"><h3>{i18n('复用说明', 'Reuse Notes')}</h3><ul class="manual-list">{''.join(notes)}</ul></div><div class="card"><h3>{i18n('资产来源', 'Asset Source')}</h3><p>{i18n('优先读取 pattern_miner 产出的 reuse_assets；缺失时回退到 workflow 和 pattern 摘要。', 'Prefers pattern_miner reuse_assets; falls back to workflow and pattern summaries when absent.')}</p></div></div><div class="asset-grid">{''.join(cards)}</div></section>'''

def _manual_layer(num: str, zh: str, en: str, text_zh: str, text_en: str, facts: list[tuple[str, Any]], items: list[str], anchor: str) -> str:
    fact_html = ''.join(f'<div><span>{escape(label)}</span><strong>{escape(value)}</strong></div>' for label, value in facts)
    item_html = ''.join(items)
    return f'<article class="manual-layer" id="{escape(anchor)}"><span class="manual-layer-num">{escape(num)}</span><div><h3>{i18n(zh, en)}</h3><p>{i18n(text_zh, text_en)}</p><div class="manual-facts">{fact_html}</div><ul class="manual-list">{item_html}</ul></div></article>'


def _label_item(label: str, value: Any) -> str:
    return f'<li><b>{escape(label)}</b> · {escape(_text_value(value) or "—")}</li>'


def _step_summary(step: Any) -> str:
    if not isinstance(step, dict):
        return _label_item('Step', step)
    name = _text_value(step.get('name', {})) or step.get('id', 'step')
    action = _text_value(step.get('action', {}))
    return _label_item(str(name), action or step.get('step_type', 'step'))


def _manual_one_liner(skill: dict[str, Any], workflow_summary: str) -> str:
    structure = skill.get('structure', {})
    skill_type = structure.get('skill_type', {}).get('primary', 'unknown')
    summary = _text_value(structure.get('summary', {}))
    return f"这是一个 {skill_type} 型 skill：{summary or workflow_summary}"[:260]


def _manual_reuse_advice(skill_type: str, reusable: list[Any], patterns: list[dict[str, Any]]) -> str:
    if patterns:
        return _text_value(patterns[0].get('definition', {})) or patterns[0].get('canonical_name') or '可抽象为复用模式。'
    if reusable:
        return '优先把 workflow、模板和验证点沉淀为可复制 checklist。'
    return f'可先沉淀为 {skill_type} 型 skill 的结构清单，再补充模板与示例。'


def _evidence_audit_panel(skill: dict[str, Any]) -> str:
    audit = skill.get("review", {}).get("evidence_audit", {}) or {}
    if not audit:
        return ""
    specs = [
        ("supported_claims", "支持结论", "Supported Claims"),
        ("inferred_claims", "推断结论", "Inferred Claims"),
        ("unsupported_claims", "不支持结论", "Unsupported Claims"),
        ("missing_evidence", "缺失证据", "Missing Evidence"),
        ("conflicts", "冲突", "Conflicts"),
    ]
    cards = []
    for key, title_zh, title_en in specs:
        values = audit.get(key, []) or []
        item_html = ''.join(f'<li>{escape(_text_value(item) or item)}</li>' for item in values[:8]) or f'<li>{i18n("暂无", "None")}</li>'
        cards.append(f'<article class="card" data-audit-kind="{escape(key)}"><h3>{i18n(title_zh, title_en)}</h3><ul class="manual-list">{item_html}</ul></article>')
    verdict = audit.get("publishable") or skill.get("review", {}).get("status", "unknown")
    rationale = audit.get("rationale") or skill.get("review", {}).get("approved_for_publish", {}).get("rationale", "")
    header = f'<div class="card feature-card"><h3>{i18n("发布建议", "Publishability")}</h3><p><strong>{escape(verdict)}</strong></p><p>{escape(rationale)}</p></div>'
    return f'<div class="two-col audit-summary">{header}<div class="card feature-card"><h3>{i18n("审计口径", "Audit Lens")}</h3><p>{i18n("区分显式支持、结构推断、缺失证据和冲突，避免把流畅总结误当事实。", "Separates explicit support, structural inference, missing evidence, and conflicts so fluent summaries are not treated as facts.")}</p></div></div><div class="asset-grid audit-grid">{"".join(cards)}</div>'


def _manual_evidence_table(skill: dict[str, Any]) -> str:
    rows: list[str] = []
    for source, claim in [('summary', skill.get('structure', {}).get('summary', {})), ('workflow', skill.get('workflow', {}).get('workflow_summary', {})), ('review', skill.get('review', {}).get('status', 'unknown'))]:
        rows.append(f'<tr><td>{escape(source)}</td><td>{escape(_text_value(claim))}</td><td>artifact</td></tr>')
    for step in (skill.get('workflow', {}).get('workflow_steps', []) or [])[:8]:
        if not isinstance(step, dict):
            continue
        evidence = step.get('evidence', []) or []
        if evidence and isinstance(evidence[0], dict):
            ev = evidence[0]
            rows.append(f'<tr><td>{escape(_text_value(step.get("name", {})) or step.get("id", "step"))}</td><td>{escape(ev.get("quote", ""))}</td><td>{escape(ev.get("source_path", "source"))} · {escape(ev.get("evidence_type", "evidence"))}</td></tr>')
    return f'<table class="evidence-table"><thead><tr><th>Claim</th><th>Evidence</th><th>Source</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'

def _section_heading(label_zh: str, label_en: str, lead_zh: str, lead_en: str, accent_zh: str, accent_en: str) -> str:
    return f'<div class="section-heading"><p class="eyebrow-label">{i18n(label_zh, label_en)}</p><h2>{i18n(lead_zh, lead_en)} <em>{i18n(accent_zh, accent_en)}</em></h2></div>'

def _page(title: str, body: str, page_type: str) -> str:
    root_prefix = ".." if page_type == "skill" else "."
    home = "../../index.html" if page_type == "skill" else "../index.html"
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>{escape(title)}</title><link rel="stylesheet" href="{root_prefix}/assets/report.css" /></head><body><main class="shell" id="top"><header class="topbar"><a class="brand" href="{home}" aria-label="Agent Skill Anatomy"><span class="brand-mark"></span><span class="brand-text">Agent Skill Anatomy</span></a><nav class="nav"><a href="{home}">{i18n('拆解首页', 'Home')}</a><a href="{root_prefix}/../cinema/">Demo</a><a href="{root_prefix}/../repo/">Repo</a><a href="{'../index.html' if page_type == 'skill' else '#'}">Report</a><a href="{root_prefix}/artifacts/">Artifacts</a><button class="lang-toggle" type="button" data-lang-toggle aria-label="Switch language">EN</button></nav></header>{body}<a class="back-to-top" href="#top">Top</a><footer class="footer">{i18n('由', 'Generated by')} <code>asa export-report</code>. {i18n('JSON artifacts 仍然是事实源。', 'JSON artifacts remain the source of truth.')}</footer></main><script src="{root_prefix}/assets/report.js"></script></body></html>\n"""


def _output_channels(output_dir: Path) -> str:
    vault_moc = output_dir.parent / "vault" / "00 Maps" / "Agent Skill Anatomy MOC.md"
    vault_launcher = output_dir.parent / "vault" / "Open in Obsidian.html"
    data_manifest = output_dir.parent / "data" / "data_manifest.json"
    graph_data = output_dir.parent / "data" / "graph-data.json"
    vault_card = _channel_card(
        channel="vault",
        title=i18n("Obsidian 学习", "Obsidian Learning"),
        description=i18n("打开完整 Markdown vault，并可选择唤起 Obsidian 作为知识库。", "Open the complete Markdown vault and optionally launch it in Obsidian."),
        status=i18n("可用", "ready") if vault_moc.exists() else i18n("需要 export-all", "generate with export-all"),
        href="../vault/Open%20in%20Obsidian.html" if vault_launcher.exists() else ("../vault/00%20Maps/Agent%20Skill%20Anatomy%20MOC.md" if vault_moc.exists() else None),
    )
    data_card = _channel_card(
        channel="data",
        title=i18n("数据研究", "Data Research"),
        description=i18n("查看 JSONL/CSV 数据集、行数清单和 benchmark 输入。", "Inspect JSONL/CSV datasets, row-count manifest, and benchmark inputs."),
        status=i18n("可用", "ready") if data_manifest.exists() else i18n("需要 export-all", "generate with export-all"),
        href="../data/" if data_manifest.exists() else None,
    )
    graph_card = _channel_card(
        channel="graph",
        title=i18n("图谱视图", "Graph View"),
        description=i18n("打开 skill、workflow、evidence、reuse 的关系图谱。", "Open the relation graph across skill, workflow, evidence, and reuse nodes."),
        status=i18n("可用", "ready") if graph_data.exists() else i18n("需要 export-data", "generate with export-data"),
        href="../graph/" if graph_data.exists() else None,
    )
    return "".join(
        [
            _channel_card("report", i18n("网页版报告", "Web Report"), i18n("阅读拆解说明书、技能页、质量门禁和原始 artifacts。", "Read the anatomy manual, skill pages, quality gates, and canonical artifacts."), i18n("当前", "active"), "#reader-guide"),
            vault_card,
            data_card,
            graph_card,
        ]
    )


def _nav_card(source: str, title_zh: str, title_en: str, href: str) -> str:
    return f'<a class="report-nav-card" href="{escape(href)}">{i18n(title_zh, title_en)}</a>'


def _channel_card(channel: str, title: str, description: str, status: str, href: str | None) -> str:
    tag = "a" if href else "div"
    href_attr = f" href=\"{href}\"" if href else ""
    disabled = " channel-disabled" if not href else ""
    return f"<{tag} class=\"channel-card{disabled}\" data-channel=\"{escape(channel)}\"{href_attr}><span>{status}</span><strong>{title}</strong><p>{description}</p></{tag}>"


def _stat(label_zh: str, label_en_or_value: Any, value: Any | None = None) -> str:
    if value is None:
        label_en = label_zh
        stat_value = label_en_or_value
    else:
        label_en = str(label_en_or_value)
        stat_value = value
    return f"<div class=\"stat\"><span>{i18n(label_zh, label_en)}</span><strong>{escape(str(stat_value))}</strong></div>"


def _skill_row(skill: dict[str, Any]) -> str:
    review = skill.get("review", {})
    approved = review.get("approved_for_publish", {}).get("value", False)
    status_class = "ok" if approved else "bad"
    return "<tr>" + f"<td><a href=\"skills/{escape(skill['id'])}.html\"><strong>{escape(skill['name'])}</strong></a><br><span class=\"muted mono\">{escape(skill['id'])}</span></td>" + f"<td><span class=\"{status_class}\">{escape(review.get('status', 'unknown'))}</span></td>" + f"<td>{i18n(str(skill.get('quality_issue_count', 0)) + ' 个问题', str(skill.get('quality_issue_count', 0)) + ' issue(s)')}</td>" + f"<td><a class=\"pill\" href=\"artifacts/skills/{escape(skill['id'])}/structure_analysis.json\">JSON</a></td>" + "</tr>"


def _issues_table(issues: list[dict[str, Any]]) -> str:
    if not issues:
        return f"<p class=\"muted\">{i18n('暂无确定性质量问题。', 'No deterministic quality issues.')}</p>"
    rows = "".join("<tr>" + f"<td>{escape(issue.get('severity', 'unknown'))}</td>" + f"<td><code>{escape(issue.get('code', 'UNKNOWN'))}</code></td>" + f"<td>{escape(issue.get('skill_id', '—'))}</td>" + f"<td>{escape(issue.get('message', issue.get('description', '')))}</td>" + "</tr>" for issue in issues[:50])
    return f"<table class=\"table\"><thead><tr><th>{i18n('严重程度', 'Severity')}</th><th>Code</th><th>Skill</th><th>{i18n('说明', 'Message')}</th></tr></thead><tbody>{rows}</tbody></table>"


def _pattern_item(pattern: dict[str, Any]) -> str:
    name = pattern.get("zh_name") or pattern.get("canonical_name") or pattern.get("id") or "Pattern"
    definition = pattern.get("definition", {})
    return f"<li><strong>{escape(name)}</strong><br><span class=\"muted\">{escape(definition.get('zh') or definition.get('en') or '')}</span></li>"


def _step_item(step: dict[str, Any]) -> str:
    if not isinstance(step, dict):
        return f'<li><span class="pill">step</span> <strong>{escape(str(step))}</strong></li>'
    name = step.get("name", {})
    action = step.get("action", {})
    confidence = step.get("confidence", "unknown")
    inferred = " inferred" if step.get("inferred") else ""
    return f'<li><span class="pill">{escape(step.get("id", "step"))}</span> <strong>{escape(_text_value(name) or "Unnamed step")}</strong><br><span class="muted">{escape(_text_value(action))}</span><br><span class="muted mono">confidence={escape(confidence)}{escape(inferred)}</span></li>'


def _review_issue(issue: dict[str, Any]) -> str:
    if not isinstance(issue, dict):
        return f'<li><span class="pill">review</span> {escape(str(issue))}</li>'
    description = issue.get("description", {})
    return f'<li><span class="pill">{escape(issue.get("severity", "unknown"))}</span> {escape(_text_value(description) or str(issue))}</li>'

def _artifact_link(run_dir: Path, artifact_path: Path) -> str:
    if not artifact_path.exists():
        return ""
    rel = artifact_path.relative_to(run_dir).as_posix()
    return f"<li><a href=\"../artifacts/{escape(rel)}\"><code>{escape(rel)}</code></a></li>"


def _format_counts(counts: dict[str, Any]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _copy_artifacts(run_dir: Path, artifacts_dir: Path) -> None:
    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)
    shutil.copytree(run_dir, artifacts_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def _read_optional_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return read_json(path)


def i18n(zh: Any, en: Any) -> str:
    zh_text = escape(zh)
    en_text = escape(en)
    return f'<span data-i18n data-zh="{zh_text}" data-en="{en_text}">{zh_text}</span>'


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)
