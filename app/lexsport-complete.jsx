import { useState, useEffect, useRef } from "react";

// ═══════════════════════════════════════════════════════════════════
// LEXSPORT COMPLETE PLATFORM — All 9 Modules
// Aesthetic: Dark Obsidian × Champagne Gold × Editorial Serif
// ═══════════════════════════════════════════════════════════════════

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,600&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{
  --bg:#09090b;--bg2:#0f1013;--bg3:#141618;--bg4:#1a1d22;
  --glass:rgba(255,255,255,0.033);--glass2:rgba(255,255,255,0.055);
  --gold:#c9a84c;--gold2:#e8c96a;--gold3:rgba(201,168,76,0.18);--gold4:rgba(201,168,76,0.07);
  --text:#ede9e1;--text2:#8a8478;--text3:#4a4840;
  --border:rgba(255,255,255,0.07);--border2:rgba(201,168,76,0.25);
  --red:#e05555;--orange:#e09544;--yellow:#d4c84a;--green:#4ec87a;--blue:#4a8fe0;--purple:#9a55e0;
  --r:rgba(224,85,85,.12);--o:rgba(224,149,68,.12);--y:rgba(212,200,74,.10);--g:rgba(78,200,122,.10);--b:rgba(74,143,224,.10);--p:rgba(154,85,224,.10);
}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;}
.app{min-height:100vh;background:var(--bg);position:relative;overflow-x:hidden;}
.bg-mesh{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.orb{position:absolute;border-radius:50%;filter:blur(130px);opacity:.05;}
.orb1{width:700px;height:700px;background:#c9a84c;top:-250px;right:-150px;animation:o1 20s ease-in-out infinite;}
.orb2{width:500px;height:500px;background:#4a8fe0;bottom:-150px;left:-100px;animation:o2 25s ease-in-out infinite;}
.orb3{width:350px;height:350px;background:#4ec87a;top:45%;left:45%;animation:o3 18s ease-in-out infinite;}
@keyframes o1{0%,100%{transform:translate(0,0)}50%{transform:translate(-50px,35px)}}
@keyframes o2{0%,100%{transform:translate(0,0)}50%{transform:translate(35px,-45px)}}
@keyframes o3{0%,100%{transform:translate(0,0)}50%{transform:translate(-25px,25px)}}
.bg-grid{position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(255,255,255,.012) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.012) 1px,transparent 1px);
  background-size:64px 64px;}

/* NAV */
.nav{position:sticky;top:0;z-index:300;height:54px;background:rgba(9,9,11,.88);backdrop-filter:blur(24px);
  border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 1.5rem;gap:0;}
.logo{font-family:'Cormorant Garamond',serif;font-size:1.3rem;font-weight:600;letter-spacing:2px;
  color:var(--text);margin-right:2rem;display:flex;align-items:center;gap:8px;white-space:nowrap;flex-shrink:0;}
.logo em{color:var(--gold);font-style:italic;}
.logo-dot{width:6px;height:6px;border-radius:50%;background:var(--gold);
  animation:logoPulse 2s ease-in-out infinite;box-shadow:0 0 8px var(--gold);}
@keyframes logoPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.7)}}
.nav-tabs{display:flex;align-items:stretch;flex:1;overflow-x:auto;gap:0;}
.ntab{display:flex;align-items:center;gap:6px;padding:0 14px;height:54px;
  font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--text3);border:none;background:transparent;cursor:pointer;white-space:nowrap;
  border-bottom:2px solid transparent;transition:all .2s;}
.ntab:hover{color:var(--text2);}
.ntab.active{color:var(--gold);border-bottom-color:var(--gold);}
.ntab .nbadge{background:var(--red);color:#fff;border-radius:8px;padding:1px 5px;font-size:7px;line-height:1.5;}
.nav-r{display:flex;align-items:center;gap:10px;margin-left:auto;padding-left:1.5rem;flex-shrink:0;}
.nav-time{font-family:'DM Mono',monospace;font-size:9px;color:var(--text3);letter-spacing:1px;}
.nav-av{width:28px;height:28px;border-radius:50%;background:var(--gold3);border:1px solid var(--border2);
  display:flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:9px;color:var(--gold);cursor:pointer;}

/* SHARED */
.page{position:relative;z-index:1;padding:1.75rem 1.75rem 4rem;max-width:1180px;margin:0 auto;animation:pu .4s ease;}
@keyframes pu{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.page-header{margin-bottom:1.5rem;}
.page-eyebrow{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin-bottom:8px;}
.page-title{font-family:'Cormorant Garamond',serif;font-size:clamp(1.6rem,3vw,2.4rem);font-weight:300;color:var(--text);line-height:1.1;}
.page-title em{color:var(--gold);font-style:italic;}
.page-sub{font-size:13px;color:var(--text2);margin-top:6px;line-height:1.6;}
.section-label{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;
  color:var(--text3);margin-bottom:1rem;display:flex;align-items:center;gap:10px;}
.section-label::after{content:'';flex:1;height:1px;background:var(--border);}
.card{background:var(--glass);border:1px solid var(--border);border-radius:10px;overflow:hidden;transition:border-color .2s;}
.card:hover{border-color:rgba(255,255,255,.12);}
.card-header{padding:.875rem 1.25rem;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;gap:8px;}
.card-title{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2.5px;text-transform:uppercase;color:var(--text3);}
.card-body{padding:1.25rem;}
.btn{display:inline-flex;align-items:center;gap:7px;padding:8px 16px;border-radius:6px;border:none;
  font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .2s;}
.btn-gold{background:var(--gold);color:var(--bg);}
.btn-gold:hover{background:var(--gold2);}
.btn-gold:disabled{opacity:.4;cursor:not-allowed;}
.btn-ghost{background:transparent;color:var(--text2);border:1px solid var(--border);}
.btn-ghost:hover{color:var(--gold);border-color:var(--border2);}
.btn-ghost:disabled{opacity:.3;cursor:not-allowed;}
.input{width:100%;padding:10px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:6px;
  color:var(--text);font-family:'DM Sans',sans-serif;font-size:13px;outline:none;transition:border-color .2s;}
.input:focus{border-color:var(--border2);}
.input::placeholder{color:var(--text3);}
.select{padding:8px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:6px;
  color:var(--text2);font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;outline:none;cursor:pointer;}
.tag{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:4px;
  font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;border:1px solid;}
.tag-red{color:var(--red);border-color:rgba(224,85,85,.3);background:var(--r);}
.tag-orange{color:var(--orange);border-color:rgba(224,149,68,.3);background:var(--o);}
.tag-yellow{color:var(--yellow);border-color:rgba(212,200,74,.3);background:var(--y);}
.tag-green{color:var(--green);border-color:rgba(78,200,122,.3);background:var(--g);}
.tag-blue{color:var(--blue);border-color:rgba(74,143,224,.3);background:var(--b);}
.tag-gold{color:var(--gold);border-color:var(--border2);background:var(--gold4);}
.dots{display:inline-flex;gap:4px;align-items:center;}
.dot{width:5px;height:5px;border-radius:50%;background:var(--gold);animation:dp 1s ease-in-out infinite;}
@keyframes dp{0%,100%{opacity:.2;transform:scale(.6)}50%{opacity:1;transform:scale(1)}}
textarea.input{resize:vertical;font-family:'DM Mono',monospace;font-size:12px;line-height:1.7;}
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.08);border-radius:2px}

/* ── HOME ── */
.home-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem;}
.mod-card{background:var(--glass);border:1px solid var(--border);border-radius:10px;padding:1.25rem;
  cursor:pointer;transition:all .25s;position:relative;overflow:hidden;animation:pu .5s ease both;}
.mod-card::after{content:'';position:absolute;inset:0;border-radius:10px;
  background:linear-gradient(135deg,var(--glass2),transparent 60%);opacity:0;transition:opacity .25s;}
.mod-card:hover{border-color:var(--border2);transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,.4);}
.mod-card:hover::after{opacity:1;}
.mod-icon{font-size:1.5rem;margin-bottom:.875rem;display:block;}
.mod-name{font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:500;color:var(--text);margin-bottom:4px;}
.mod-desc{font-size:12px;color:var(--text2);line-height:1.6;margin-bottom:1rem;}
.mod-stats{display:flex;gap:1rem;}
.mstat-val{font-family:'DM Mono',monospace;font-size:.875rem;color:var(--gold);line-height:1;}
.mstat-lbl{font-family:'DM Mono',monospace;font-size:7px;color:var(--text3);letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;}
.mod-arrow{position:absolute;bottom:1.25rem;right:1.25rem;font-family:'DM Mono',monospace;font-size:10px;color:var(--text3);transition:all .2s;}
.mod-card:hover .mod-arrow{color:var(--gold);transform:translateX(3px);}
.home-bottom{display:grid;grid-template-columns:1fr 300px;gap:1rem;}
.activity-row{display:flex;align-items:flex-start;gap:10px;padding:.75rem 1.25rem;border-bottom:1px solid var(--border);transition:background .15s;}
.activity-row:hover{background:var(--glass2);}
.activity-row:last-child{border-bottom:none;}
.adot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:5px;}
.a-title{font-size:12px;color:var(--text);line-height:1.4;margin-bottom:1px;}
.a-sub{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;}
.a-time{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);white-space:nowrap;flex-shrink:0;}
.dl-row{display:flex;align-items:center;gap:10px;padding:.625rem 1.25rem;border-bottom:1px solid var(--border);}
.dl-row:last-child{border-bottom:none;}
.dl-days{font-family:'DM Mono',monospace;font-size:.9rem;font-weight:500;min-width:28px;text-align:center;line-height:1;}
.dl-lbl{font-family:'DM Mono',monospace;font-size:7px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;text-align:center;}
.dl-div{width:1px;height:28px;background:var(--border);flex-shrink:0;}
.dl-name{font-size:11px;color:var(--text);line-height:1.3;}
.dl-type{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;margin-top:1px;}
.briefing-wrap{background:var(--glass);border:1px solid var(--border2);border-radius:10px;
  padding:1.5rem;margin-top:1rem;position:relative;overflow:hidden;}
.briefing-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--gold),transparent);}
.briefing-text{font-family:'Cormorant Garamond',serif;font-size:1rem;font-weight:300;
  color:var(--text2);line-height:1.85;white-space:pre-wrap;margin-top:.75rem;}

/* ── CONTRACTS ── */
.risk-meter{height:6px;background:var(--border);border-radius:3px;overflow:hidden;margin-top:6px;}
.risk-meter-fill{height:100%;border-radius:3px;transition:width 1s ease;}
.clause-card{border-left:3px solid;padding:.875rem 1rem;border-radius:0 6px 6px 0;
  background:var(--glass);margin-bottom:.75rem;}
.clause-card.critical{border-color:var(--red);}
.clause-card.high{border-color:var(--orange);}
.clause-card.medium{border-color:var(--yellow);}
.clause-card.low{border-color:var(--green);}
.clause-title{font-size:13px;font-weight:500;color:var(--text);margin-bottom:3px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
.clause-body{font-size:12px;color:var(--text2);line-height:1.65;}
.clause-rec{font-size:11px;color:var(--text3);margin-top:5px;font-style:italic;}

/* ── RESEARCH ── */
.qchip{padding:5px 12px;background:var(--glass);border:1px solid var(--border);border-radius:20px;
  color:var(--text2);font-size:11px;font-family:'Cormorant Garamond',serif;font-style:italic;
  cursor:pointer;transition:all .15s;white-space:nowrap;}
.qchip:hover{background:var(--glass2);border-color:var(--border2);color:var(--gold);}
.result-card{background:var(--glass);border:1px solid var(--border);border-radius:10px;overflow:hidden;animation:pu .3s ease;margin-bottom:1rem;}
.result-header{background:var(--glass2);padding:.875rem 1.25rem;border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.result-query{font-family:'Cormorant Garamond',serif;font-size:.95rem;font-style:italic;color:var(--text2);flex:1;}
.result-body{padding:1.25rem 1.5rem;font-size:14px;line-height:1.82;color:var(--text2);white-space:pre-wrap;font-family:'Cormorant Garamond',serif;}

/* ── LEADS ── */
.lead-card{background:var(--glass);border:1px solid var(--border);border-radius:8px;
  padding:1rem 1.25rem;cursor:pointer;transition:all .2s;position:relative;overflow:hidden;margin-bottom:.75rem;}
.lead-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;}
.lead-card.urgent::before{background:var(--red);box-shadow:0 0 8px var(--red);}
.lead-card.high::before{background:var(--orange);}
.lead-card.medium::before{background:var(--yellow);}
.lead-card.low::before{background:var(--green);}
.lead-card:hover,.lead-card.sel{border-color:var(--border2);background:var(--glass2);}
.lead-name{font-size:14px;font-weight:500;color:var(--text);}
.lead-sport{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;margin-top:1px;}
.lead-issue{font-size:12px;color:var(--text2);line-height:1.5;margin:.5rem 0;}
.lead-val{font-family:'DM Mono',monospace;font-size:11px;color:var(--gold);}
.outreach-box{background:var(--bg2);border:1px solid var(--border);border-radius:8px;overflow:hidden;}
.outreach-text{padding:1rem 1.25rem;font-size:13px;line-height:1.75;color:var(--text2);white-space:pre-wrap;min-height:200px;}
.tone-btn{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;
  padding:3px 8px;border-radius:4px;border:1px solid var(--border);background:transparent;
  color:var(--text3);cursor:pointer;transition:all .15s;}
.tone-btn:hover{color:var(--gold);border-color:var(--border2);}
.tone-btn.act{color:var(--gold);border-color:var(--border2);background:var(--gold4);}

/* ── DOCUMENTS ── */
.doc-type-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:1.25rem;}
.doc-type-btn{padding:.875rem;background:var(--glass);border:1px solid var(--border);border-radius:8px;
  cursor:pointer;transition:all .2s;text-align:left;}
.doc-type-btn:hover{border-color:var(--border2);}
.doc-type-btn.act{border-color:var(--gold);background:var(--gold4);}
.doc-type-icon{font-size:1.1rem;margin-bottom:5px;display:block;}
.doc-type-name{font-size:12px;font-weight:500;color:var(--text);margin-bottom:2px;}
.doc-type-sub{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;}
.doc-result{background:var(--bg2);border:1px solid var(--border);border-radius:8px;
  padding:1.25rem 1.5rem;font-family:'DM Mono',monospace;font-size:12px;
  line-height:1.8;color:var(--text2);white-space:pre-wrap;max-height:500px;overflow-y:auto;margin-top:1rem;}

/* ── CALENDAR ── */
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;margin-bottom:1.25rem;}
.cal-day-header{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--text3);text-align:center;padding:6px 0;}
.cal-cell{min-height:72px;background:var(--glass);border:1px solid var(--border);border-radius:4px;
  padding:4px;cursor:pointer;transition:background .15s;position:relative;}
.cal-cell:hover{background:var(--glass2);}
.cal-cell.today{border-color:var(--gold);}
.cal-cell.other-month{opacity:.35;}
.cal-num{font-family:'DM Mono',monospace;font-size:10px;color:var(--text2);margin-bottom:3px;text-align:right;}
.cal-num.today-num{color:var(--gold);font-weight:500;}
.cal-event{font-size:9px;padding:2px 4px;border-radius:2px;margin-bottom:2px;line-height:1.3;
  overflow:hidden;white-space:nowrap;text-overflow:ellipsis;}
.cal-event.cas{background:var(--r);color:var(--red);}
.cal-event.contract{background:var(--b);color:var(--blue);}
.cal-event.deadline{background:var(--o);color:var(--orange);}
.cal-event.hearing{background:var(--p);color:var(--purple);}
.upcoming-item{display:flex;align-items:flex-start;gap:12px;padding:.75rem 1.25rem;
  border-bottom:1px solid var(--border);transition:background .15s;}
.upcoming-item:hover{background:var(--glass2);}
.upcoming-item:last-child{border-bottom:none;}
.up-date{min-width:44px;text-align:center;padding:6px;background:var(--glass2);border-radius:6px;}
.up-day{font-family:'DM Mono',monospace;font-size:1rem;font-weight:500;line-height:1;}
.up-month{font-family:'DM Mono',monospace;font-size:7px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;}
.up-title{font-size:13px;color:var(--text);margin-bottom:2px;}
.up-sub{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;}

/* ── PIPELINE ── */
.kanban{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;align-items:start;}
.kanban-col{background:var(--glass);border:1px solid var(--border);border-radius:10px;overflow:hidden;}
.kanban-col-header{padding:.875rem 1rem;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;}
.kanban-col-title{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:var(--text3);}
.kanban-count{font-family:'DM Mono',monospace;font-size:10px;color:var(--gold);background:var(--gold4);
  padding:1px 6px;border-radius:8px;border:1px solid var(--border2);}
.kanban-body{padding:.75rem;display:flex;flex-direction:column;gap:.625rem;}
.kcard{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:.875rem;
  cursor:default;transition:border-color .2s;}
.kcard:hover{border-color:rgba(255,255,255,.12);}
.kcard-name{font-size:13px;font-weight:500;color:var(--text);margin-bottom:2px;}
.kcard-type{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;}
.kcard-val{font-family:'DM Mono',monospace;font-size:11px;color:var(--gold);margin-top:6px;}
.kcard-due{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);margin-top:3px;}
.revenue-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem;}
.rev-stat{background:var(--glass);border:1px solid var(--border);border-radius:10px;padding:1.25rem;}
.rev-stat-val{font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:500;color:var(--gold);line-height:1;}
.rev-stat-label{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:2px;text-transform:uppercase;margin-top:5px;}
.rev-stat-change{font-family:'DM Mono',monospace;font-size:9px;margin-top:4px;}

/* ── CLIENTS ── */
.client-grid{display:grid;grid-template-columns:240px 1fr;gap:1rem;min-height:520px;}
.client-list{background:var(--glass);border:1px solid var(--border);border-radius:10px;overflow:hidden;}
.client-item{display:flex;align-items:center;gap:10px;padding:.75rem 1rem;border-bottom:1px solid var(--border);
  cursor:pointer;transition:background .15s;}
.client-item:hover,.client-item.sel{background:var(--glass2);}
.client-item:last-child{border-bottom:none;}
.client-av{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-family:'Cormorant Garamond',serif;font-size:.875rem;font-weight:600;flex-shrink:0;border:1px solid var(--border);}
.client-name-small{font-size:13px;color:var(--text);font-weight:500;}
.client-sport-small{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;margin-top:1px;}
.client-detail{background:var(--glass);border:1px solid var(--border);border-radius:10px;overflow:hidden;}
.cd-hero{padding:1.5rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:1rem;}
.cd-av-lg{width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-family:'Cormorant Garamond',serif;font-size:1.4rem;font-weight:600;border:1px solid var(--border);flex-shrink:0;}
.cd-name{font-family:'Cormorant Garamond',serif;font-size:1.4rem;font-weight:500;color:var(--text);}
.cd-sub{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;}
.cd-body{padding:1.25rem;display:flex;flex-direction:column;gap:1.25rem;}
.cd-section-title{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;
  color:var(--text3);margin-bottom:.75rem;border-bottom:1px solid var(--border);padding-bottom:6px;}
.case-row{display:flex;align-items:center;gap:10px;padding:.625rem 0;border-bottom:1px solid var(--border);}
.case-row:last-child{border-bottom:none;}
.case-name{font-size:12px;color:var(--text);flex:1;}
.case-type-sm{font-family:'DM Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1px;}
.chat-messages{display:flex;flex-direction:column;gap:.75rem;padding:1rem;max-height:240px;overflow-y:auto;}
.chat-msg{display:flex;}
.chat-msg.user{justify-content:flex-end;}
.chat-bubble{max-width:80%;padding:.625rem .875rem;border-radius:10px;font-size:13px;line-height:1.6;}
.chat-bubble.ai{background:var(--glass2);border:1px solid var(--border);color:var(--text2);border-radius:4px 10px 10px 10px;}
.chat-bubble.user{background:var(--gold3);border:1px solid var(--border2);color:var(--text);border-radius:10px 4px 10px 10px;}
.chat-input-row{display:flex;gap:8px;padding:.875rem 1rem;border-top:1px solid var(--border);}

@media(max-width:900px){
  .home-grid{grid-template-columns:1fr 1fr;}
  .kanban{grid-template-columns:1fr 1fr;}
  .doc-type-grid{grid-template-columns:1fr 1fr;}
  .revenue-grid{grid-template-columns:1fr 1fr;}
  .client-grid{grid-template-columns:1fr;}
  .home-bottom{grid-template-columns:1fr;}
}
@media(max-width:600px){
  .home-grid{grid-template-columns:1fr;}
  .page{padding:1rem 1rem 3rem;}
}
`;

// ── DATA ──────────────────────────────────────────────────────────────────────
const MODULES = [
  {id:"contracts",icon:"⚖️",name:"Contract Analyzer",desc:"AI risk reports for any sports contract across all leagues, genders, and sports.",stats:[{v:"38",l:"Analyzed"},{v:"78",l:"Avg Risk"},{v:"4",l:"Languages"}],color:"var(--red)"},
  {id:"research",icon:"🔍",name:"Case Research",desc:"CAS, FIFA, WADA, and all sports law domains. Senior attorney-level answers instantly.",stats:[{v:"14",l:"Domains"},{v:"240+",l:"Sources"},{v:"CAS",l:"Jurisprudence"}],color:"var(--blue)"},
  {id:"leads",icon:"📡",name:"Lead Radar",desc:"Live athlete opportunity feed with AI-generated personalised outreach emails.",stats:[{v:"12",l:"Signals"},{v:"$28M",l:"Pipeline"},{v:"2",l:"Urgent"}],color:"var(--green)"},
  {id:"documents",icon:"📄",name:"Document Generator",desc:"Draft contracts, NDAs, demand letters, and arbitration filings in seconds.",stats:[{v:"40+",l:"Doc Types"},{v:"AI",l:"Powered"},{v:"Fast",l:"Draft"}],color:"var(--gold)"},
  {id:"calendar",icon:"📅",name:"Deadline Calendar",desc:"Visual case timeline with auto-alerts. Never miss a CAS filing or transfer window.",stats:[{v:"8",l:"Deadlines"},{v:"3",l:"This Week"},{v:"Auto",l:"Alerts"}],color:"var(--purple)"},
  {id:"pipeline",icon:"💰",name:"Revenue Pipeline",desc:"Kanban case board, billing tracker, revenue forecasts, and win/loss analytics.",stats:[{v:"$2.1M",l:"Active"},{v:"18",l:"Cases"},{v:"87%",l:"Win Rate"}],color:"var(--orange)"},
  {id:"clients",icon:"👤",name:"Client Manager",desc:"Full client profiles, case history, document vault, and AI chat portal.",stats:[{v:"24",l:"Clients"},{v:"98%",l:"Retention"},{v:"24/7",l:"AI Chat"}],color:"var(--yellow)"},
];

const ACTIVITY = [
  {c:"var(--red)",t:"Contract risk report generated",s:"Marcus Adeyemi / Atletico FC · Risk 78/100",time:"2m ago"},
  {c:"var(--green)",t:"New urgent lead detected",s:"Darius Cole · NFL franchise tag · $18.4M",time:"8m ago"},
  {c:"var(--blue)",t:"Case research completed",s:"FIFA RSTP Art. 17 unilateral termination",time:"34m ago"},
  {c:"var(--gold)",t:"Outreach email sent",s:"Yasmin Al-Rashid · WTA doping appeal",time:"1h ago"},
  {c:"var(--purple)",t:"CAS filing deadline approaching",s:"Aiko Tanaka — 10 days remaining",time:"2h ago"},
  {c:"var(--orange)",t:"Invoice sent — €12,400",s:"FC Santos Youth Academy",time:"3h ago"},
];

const DEADLINES = [
  {d:2,n:"CAS appeal — Yasmin Al-Rashid WADA TUE",t:"ANTI-DOPING",c:"var(--red)"},
  {d:7,n:"NFL franchise tag response — Darius Cole",t:"CONTRACT · NFL",c:"var(--red)"},
  {d:10,n:"Non-compete challenge — Aiko Tanaka",t:"ESPORTS · RESTRAINT",c:"var(--orange)"},
  {d:14,n:"FIFA training comp — LAFC Academy",t:"TRANSFER · FIFA",c:"var(--orange)"},
  {d:21,n:"TPO dispute filing — FC Santos",t:"THIRD PARTY OWNERSHIP",c:"var(--yellow)"},
  {d:28,n:"ITC request — Priya Sharma",t:"NATIONALITY · WA",c:"var(--yellow)"},
];

const LEADS_DATA = [
  {id:1,name:"Darius Cole",sport:"NFL",issue:"Franchise tag dispute — Pro Bowl WR seeking long-term deal.",urgency:"urgent",time:"8m",value:"$18.4M",detail:"3rd-year WR. Club invoking franchise tag 2nd consecutive year. Bad-faith negotiation alleged."},
  {id:2,name:"Yasmin Al-Rashid",sport:"WTA Tennis",issue:"WADA TUE denied — ADHD medication Adderall prescribed.",urgency:"urgent",time:"22m",value:"$3.1M",detail:"World No.34. CAS appeal window open 14 days. Strong medical documentation."},
  {id:3,name:"FC Santos Youth",sport:"Football / Brasileirão",issue:"Third-party ownership — academy player economic rights sold illegally.",urgency:"high",time:"1h",value:"$2.2M",detail:"17yo striker. FIFA Art. 18ter violation. Offshore fund claiming rights."},
  {id:4,name:"Marcus Osei",sport:"Football / La Liga",issue:"Image rights breach — NFT collection without consent.",urgency:"high",time:"2h",value:"$890K",detail:"Club minted 4,200 NFT units at €200 each. No image rights clause in contract."},
  {id:5,name:"Aiko Tanaka",sport:"Esports / Valorant",issue:"Non-compete preventing post-contract club signing.",urgency:"high",time:"3h",value:"$620K",detail:"IGL with expired contract. Org citing 6-month non-compete. Rival team LOI signed."},
];

const DOC_TYPES = [
  {icon:"📋",name:"Player Employment Agreement",sub:"Full Contract"},
  {icon:"🤝",name:"Representation Agreement",sub:"Agent · FIFA Licensed"},
  {icon:"🖼️",name:"Image Rights License",sub:"Commercial · NFT"},
  {icon:"🔒",name:"NDA / Confidentiality",sub:"Mutual · One-Way"},
  {icon:"⚡",name:"Arbitration Demand Letter",sub:"CAS · Domestic"},
  {icon:"💸",name:"Endorsement Contract",sub:"Sponsorship · Brand"},
  {icon:"🎮",name:"Esports Roster Agreement",sub:"Team · Streaming"},
  {icon:"🏥",name:"Settlement Agreement",sub:"Dispute Resolution"},
  {icon:"📑",name:"Transfer Agreement",sub:"Permanent · Loan"},
];

const CAL_EVENTS = {
  "2025-06-02":[{title:"CAS — Rashid TUE",type:"cas"}],
  "2025-06-05":[{title:"Osei NFT hearing",type:"contract"}],
  "2025-06-07":[{title:"NFL tag deadline",type:"deadline"}],
  "2025-06-10":[{title:"Santos TPO filing",type:"deadline"}],
  "2025-06-12":[{title:"Tanaka hearing",type:"hearing"}],
  "2025-06-15":[{title:"CAS appeal — Cole",type:"cas"},{title:"Sharma ITC",type:"contract"}],
  "2025-06-18":[{title:"WADA review",type:"cas"}],
  "2025-06-20":[{title:"La Liga arbitration",type:"hearing"}],
  "2025-06-25":[{title:"Training comp claim",type:"deadline"}],
};

const PIPELINE_COLS = [
  {id:"prospect",title:"Prospect",color:"var(--text3)",cases:[
    {name:"Storm Nakamura",type:"Streaming Rights",val:"$210K",due:"No deadline"},
    {name:"Sofia Eriksson",type:"LIV Golf Rules",val:"$1.9M",due:"Flexible"},
  ]},
  {id:"active",title:"Active",color:"var(--blue)",cases:[
    {name:"Yasmin Al-Rashid",type:"Anti-Doping / CAS",val:"$3.1M",due:"14 days"},
    {name:"FC Santos Youth",type:"TPO Dispute",val:"$2.2M",due:"21 days"},
    {name:"Kwame Asante",type:"Contract Termination",val:"$2.8M",due:"30 days"},
  ]},
  {id:"negotiation",title:"Negotiating",color:"var(--gold)",cases:[
    {name:"Darius Cole",type:"NFL Franchise Tag",val:"$18.4M",due:"7 days"},
    {name:"Marcus Osei",type:"Image Rights",val:"$890K",due:"30 days"},
    {name:"Aiko Tanaka",type:"Non-Compete",val:"$620K",due:"10 days"},
  ]},
  {id:"closed",title:"Closed Won",color:"var(--green)",cases:[
    {name:"LAFC Academy",type:"Training Comp",val:"$340K",due:"Settled"},
    {name:"Priya Sharma",type:"ITC · World Athletics",val:"$280K",due:"Resolved"},
  ]},
];

const CLIENTS = [
  {id:1,name:"Darius Cole",sport:"NFL",flag:"🏈",color:"#e05555",bg:"rgba(224,85,85,.15)",cases:["NFL Franchise Tag Dispute","2023 Endorsement Review"],val:"$18.4M",status:"Active"},
  {id:2,name:"Yasmin Al-Rashid",sport:"WTA Tennis",flag:"🎾",color:"#e09544",bg:"rgba(224,149,68,.15)",cases:["WADA TUE Appeal","Image Rights — Adidas"],val:"$3.1M",status:"Urgent"},
  {id:3,name:"Aiko Tanaka",sport:"Esports",flag:"🎮",color:"#9a55e0",bg:"rgba(154,85,224,.15)",cases:["Non-Compete Challenge","Streaming Contract Review"],val:"$620K",status:"Active"},
  {id:4,name:"Marcus Osei",sport:"La Liga",flag:"⚽",color:"#4ec87a",bg:"rgba(78,200,122,.15)",cases:["NFT Image Rights Breach","Contract Renegotiation"],val:"$890K",status:"Active"},
  {id:5,name:"FC Santos Youth",sport:"Brasileirão",flag:"⚽",color:"#4a8fe0",bg:"rgba(74,143,224,.15)",cases:["TPO Dispute","Youth Transfer Protocol"],val:"$2.2M",status:"Negotiating"},
];

// ── HELPERS ───────────────────────────────────────────────────────────────────
function Clock(){
  const [t,setT]=useState(()=>new Date().toLocaleTimeString("en-GB",{hour:"2-digit",minute:"2-digit",second:"2-digit"}));
  useEffect(()=>{const iv=setInterval(()=>setT(new Date().toLocaleTimeString("en-GB",{hour:"2-digit",minute:"2-digit",second:"2-digit"})),1000);return()=>clearInterval(iv);},[]);
  return <span className="nav-time">{t}</span>;
}
function Dots(){return <span className="dots">{[0,1,2].map(i=><span key={i} className="dot" style={{animationDelay:`${i*.18}s`}}/>)}</span>;}
function riskColor(l){return{critical:"var(--red)",high:"var(--orange)",medium:"var(--yellow)",low:"var(--green)"}[l]||"var(--text3)";}
function riskTag(l){return{critical:"tag-red",high:"tag-orange",medium:"tag-yellow",low:"tag-green"}[l]||"tag-gold";}

function useTypewriter(text,speed=14,active=false){
  const [out,setOut]=useState("");
  const [done,setDone]=useState(false);
  useEffect(()=>{
    if(!active||!text)return;
    setOut("");setDone(false);let i=0;
    const iv=setInterval(()=>{setOut(text.slice(0,++i));if(i>=text.length){clearInterval(iv);setDone(true);}},speed);
    return()=>clearInterval(iv);
  },[text,active]);
  return{out,done};
}

// ── PAGES ─────────────────────────────────────────────────────────────────────

// HOME
function Home({onNav}){
  const [briefing,setBriefing]=useState("");
  const [bl,setBl]=useState(false);
  const tw=useTypewriter(briefing,12,!!briefing);

  async function genBriefing(){
    setBl(true);setBriefing("");
    try{
      const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:700,messages:[{role:"user",content:"You are a senior sports law partner. Write a 3-paragraph daily morning briefing for your team covering: (1) pressing global sports law developments this week, (2) key FIFA/WADA/esports regulatory updates, (3) one strategic opportunity for sports lawyers right now. Be specific, authoritative, and insightful."}]})});
      const d=await r.json();
      setBriefing(d.content?.map(b=>b.text||"").join("")||"Briefing unavailable.");
    }catch{setBriefing("Connection error.");}
    setBl(false);
  }

  return(
    <div className="page">
      <div className="page-header">
        <div className="page-eyebrow">LexSport Complete Platform · v3.0</div>
        <h1 className="page-title">Your Sports Law <em>Command Center</em></h1>
        <p className="page-sub">Seven AI-powered modules unified. Contract analysis, case research, lead generation, documents, calendar, pipeline, and client management.</p>
      </div>
      <div className="section-label">Modules</div>
      <div className="home-grid" style={{gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))"}}>
        {MODULES.map((m,i)=>(
          <div key={m.id} className="mod-card" style={{animationDelay:`${i*.07}s`}} onClick={()=>onNav(m.id)}>
            <span className="mod-icon">{m.icon}</span>
            <div className="mod-name">{m.name}</div>
            <div className="mod-desc">{m.desc}</div>
            <div className="mod-stats">{m.stats.map(s=>(
              <div key={s.l}><div className="mstat-val" style={{color:m.color}}>{s.v}</div><div className="mstat-lbl">{s.l}</div></div>
            ))}</div>
            <div className="mod-arrow">→</div>
          </div>
        ))}
      </div>
      <div className="home-bottom">
        <div className="card">
          <div className="card-header"><span className="card-title">Recent Activity</span><button className="btn btn-ghost" style={{padding:"4px 10px",fontSize:8}}>All</button></div>
          {ACTIVITY.map((a,i)=>(
            <div key={i} className="activity-row">
              <div className="adot" style={{background:a.c}}/>
              <div style={{flex:1}}><div className="a-title">{a.t}</div><div className="a-sub">{a.s}</div></div>
              <div className="a-time">{a.time}</div>
            </div>
          ))}
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">Deadlines</span></div>
          {DEADLINES.map((d,i)=>(
            <div key={i} className="dl-row">
              <div><div className="dl-days" style={{color:d.d<=7?d.c:"var(--text2)"}}>{d.d}</div><div className="dl-lbl">days</div></div>
              <div className="dl-div"/>
              <div><div className="dl-name">{d.n}</div><div className="dl-type">{d.t}</div></div>
            </div>
          ))}
        </div>
      </div>
      <div className="briefing-wrap">
        <div className="page-eyebrow" style={{marginBottom:0}}>✦ AI Morning Briefing</div>
        {briefing
          ?<div className="briefing-text">{tw.out}{!tw.done&&<span style={{opacity:.4}}>▌</span>}</div>
          :<div className="briefing-text" style={{color:"var(--text3)",fontStyle:"italic"}}>Generate your personalised daily briefing — key sports law developments, regulatory updates, and strategic opportunities.</div>}
        <button className="btn btn-ghost" style={{marginTop:"1rem"}} onClick={genBriefing} disabled={bl}>
          {bl?<><Dots/> Generating…</>:"✦ Generate Briefing"}
        </button>
      </div>
    </div>
  );
}

// CONTRACTS
function Contracts(){
  const [text,setText]=useState("");
  const [sport,setSport]=useState("Football / Soccer");
  const [cat,setCat]=useState("Men");
  const [loading,setLoading]=useState(false);
  const [result,setResult]=useState(null);

  async function analyze(){
    if(!text.trim())return;
    setLoading(true);setResult(null);
    try{
      const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:1000,messages:[{role:"user",content:`You are an elite sports law AI. Sport: ${sport}. Category: ${cat}. Analyze this contract and return ONLY valid JSON no markdown: {"riskScore":<0-100>,"overallLevel":"<critical|high|medium|low>","summary":"<3-sentence executive summary>","clauses":[{"title":"<title>","level":"<critical|high|medium|low>","finding":"<finding>","recommendation":"<rec>"}],"negotiationTips":["<tip1>","<tip2>","<tip3>","<tip4>"]}. Contract: "${text.slice(0,3000)}"`}]})});
      const d=await r.json();
      const raw=d.content?.map(b=>b.text||"").join("").replace(/```json|```/g,"").trim();
      setResult(JSON.parse(raw));
    }catch{setResult({riskScore:0,overallLevel:"low",summary:"Analysis failed. Please try again.",clauses:[],negotiationTips:[]});}
    setLoading(false);
  }

  return(
    <div className="page">
      <div className="page-header"><div className="page-eyebrow">⚖️ Contract Analyzer</div><h1 className="page-title"><em>AI Risk Analysis</em></h1><p className="page-sub">All sports · All contract types · Men, Women, Esports, Youth · 4 languages</p></div>
      <div style={{display:"flex",gap:10,marginBottom:"1rem",flexWrap:"wrap"}}>
        <select className="select" value={sport} onChange={e=>setSport(e.target.value)}>
          {["Football / Soccer","Basketball","NFL","Tennis","Esports","MMA / Boxing","Athletics","Golf","Cricket","Rugby"].map(s=><option key={s}>{s}</option>)}
        </select>
        <select className="select" value={cat} onChange={e=>setCat(e.target.value)}>
          {["Men","Women","Mixed / Open","Youth / Junior (U18)","Para / Adaptive","Esports"].map(c=><option key={c}>{c}</option>)}
        </select>
      </div>
      <div className="card" style={{marginBottom:"1rem"}}>
        <textarea className="input" rows={6} value={text} onChange={e=>setText(e.target.value)} placeholder="Paste contract text here — player agreement, endorsement deal, esports roster, NDA, transfer agreement…"/>
        <div style={{padding:".75rem 1rem",borderTop:"1px solid var(--border)",display:"flex",gap:8,alignItems:"center"}}>
          <button className="btn btn-gold" onClick={analyze} disabled={loading||!text.trim()}>{loading?<><Dots/> Analyzing…</>:"⚡ Analyze Contract"}</button>
          {text&&<button className="btn btn-ghost" onClick={()=>{setText("");setResult(null);}}>Clear</button>}
          <span style={{marginLeft:"auto",fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)"}}>{text.length} chars</span>
        </div>
      </div>
      {result&&(
        <div style={{animation:"pu .4s ease"}}>
          <div className="card" style={{marginBottom:"1rem",padding:"1.25rem"}}>
            <div style={{display:"flex",alignItems:"center",gap:"1.5rem",flexWrap:"wrap"}}>
              <div style={{textAlign:"center"}}>
                <div style={{fontFamily:"Cormorant Garamond,serif",fontSize:"3rem",fontWeight:500,color:riskColor(result.overallLevel),lineHeight:1}}>{result.riskScore}</div>
                <div style={{fontFamily:"DM Mono,monospace",fontSize:7,color:"var(--text3)",letterSpacing:2}}>/ 100 RISK</div>
              </div>
              <div style={{flex:1}}>
                <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}>
                  <span className={`tag ${riskTag(result.overallLevel)}`}>{result.overallLevel}</span>
                  <span style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1.5}}>OVERALL RISK LEVEL</span>
                </div>
                <div className="risk-meter"><div className="risk-meter-fill" style={{width:`${result.riskScore}%`,background:riskColor(result.overallLevel)}}/></div>
                <p style={{fontSize:13,color:"var(--text2)",lineHeight:1.7,marginTop:10}}>{result.summary}</p>
              </div>
            </div>
          </div>
          <div className="section-label">Clause-by-Clause Analysis</div>
          {result.clauses?.map((c,i)=>(
            <div key={i} className={`clause-card ${c.level}`}>
              <div className="clause-title"><span className={`tag ${riskTag(c.level)}`} style={{fontSize:7}}>{c.level}</span>{c.title}</div>
              <div className="clause-body">{c.finding}</div>
              {c.recommendation&&<div className="clause-rec">→ {c.recommendation}</div>}
            </div>
          ))}
          {result.negotiationTips?.length>0&&(
            <div className="card" style={{padding:"1.25rem",marginTop:"1rem"}}>
              <div className="section-label" style={{marginBottom:".75rem"}}>Negotiation Recommendations</div>
              <ol style={{paddingLeft:18,display:"flex",flexDirection:"column",gap:8}}>
                {result.negotiationTips.map((tip,i)=><li key={i} style={{fontSize:13,color:"var(--text2)",lineHeight:1.65}}>{tip}</li>)}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// RESEARCH
function Research(){
  const [q,setQ]=useState("");
  const [loading,setLoading]=useState(false);
  const [results,setResults]=useState([]);
  const QUICK=["CAS rulings — doping first offense reduction","FIFA RSTP Art. 17 unilateral termination","Bosman ruling modern impact on transfers","Esports player contract minimum standards","Women's sport equal pay litigation","UFC independent contractor classification","WADA TUE process and abuse cases","Youth academy contracts — minor protection"];

  async function search(query=q){
    if(!query.trim())return;
    setLoading(true);
    try{
      const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:1000,messages:[{role:"user",content:`You are a senior sports law research attorney. Answer at law review level. Include key legal principles, leading cases with citations, current trends (2024-2025), and practical implications for practitioners. Query: "${query}"`}]})});
      const d=await r.json();
      const text=d.content?.map(b=>b.text||"").join("")||"No result.";
      setResults(prev=>[{q:query,text,ts:new Date().toLocaleTimeString("en-GB",{hour:"2-digit",minute:"2-digit"})},...prev]);
    }catch{setResults(prev=>[{q:query,text:"Connection error. Please try again.",ts:"--:--"},...prev]);}
    setLoading(false);
  }

  return(
    <div className="page">
      <div className="page-header"><div className="page-eyebrow">🔍 Case Research</div><h1 className="page-title"><em>Legal Intelligence</em></h1><p className="page-sub">CAS jurisprudence · FIFA regulations · WADA decisions · National sports law · All domains</p></div>
      <div style={{display:"flex",background:"var(--glass)",border:"1px solid var(--border)",borderRadius:8,overflow:"hidden",marginBottom:"1rem"}}>
        <input className="input" style={{border:"none",background:"transparent",borderRadius:0}} value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==="Enter"&&search()} placeholder="Search case law, regulations, arbitration decisions, legal principles…"/>
        <button className="btn btn-gold" style={{borderRadius:0,borderLeft:"1px solid var(--border)"}} onClick={()=>search()} disabled={loading||!q.trim()}>{loading?<Dots/>:"→ Research"}</button>
      </div>
      <div style={{display:"flex",flexWrap:"wrap",gap:8,marginBottom:"1.25rem"}}>
        {QUICK.map((s,i)=><button key={i} className="qchip" onClick={()=>{setQ(s);search(s);}}>{s}</button>)}
      </div>
      {loading&&<div style={{textAlign:"center",padding:"2rem",fontFamily:"DM Mono,monospace",fontSize:10,color:"var(--text3)",letterSpacing:2}}>RESEARCHING PRECEDENTS <Dots/></div>}
      {results.map((r,i)=>(
        <div key={i} className="result-card">
          <div className="result-header">
            <span className="result-query">"{r.q}"</span>
            <span style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)"}}>{r.ts}</span>
            <button className="btn btn-ghost" style={{padding:"3px 10px",fontSize:8}} onClick={()=>navigator.clipboard.writeText(r.text)}>Copy</button>
          </div>
          <div className="result-body">{r.text}</div>
        </div>
      ))}
      {results.length===0&&!loading&&<div style={{textAlign:"center",padding:"3rem",color:"var(--text3)",fontFamily:"Cormorant Garamond,serif",fontSize:"1.1rem",fontStyle:"italic"}}>Enter a query or click a quick search above to begin…</div>}
    </div>
  );
}

// LEADS
function Leads(){
  const [sel,setSel]=useState(null);
  const [tone,setTone]=useState("Professional");
  const [outreach,setOutreach]=useState("");
  const [loading,setLoading]=useState(false);
  const [copied,setCopied]=useState(false);
  const TONES=["Professional","Urgent","Consultative","Cold Outreach"];
  const toneMap={Professional:"formal, authoritative, senior counsel tone",Urgent:"urgent and time-sensitive, emphasize deadline risk",Consultative:"warm, advisory, trusted advisor",["Cold Outreach"]:"concise cold outreach under 120 words with strong hook"};

  async function gen(lead,t){
    setLoading(true);setOutreach("");
    try{
      const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:700,messages:[{role:"user",content:`Write a ${toneMap[t]} outreach email from LexSport Law Group to ${lead.name} (${lead.sport}) about: "${lead.issue}". Additional context: ${lead.detail}. Include Subject line, personalised body referencing their exact situation, and professional sign-off. Use their actual name.`}]})});
      const d=await r.json();
      setOutreach(d.content?.map(b=>b.text||"").join("")||"Generation failed.");
    }catch{setOutreach("Connection error.");}
    setLoading(false);
  }

  function select(lead){setSel(lead);setOutreach("");gen(lead,tone);}
  function changeTone(t){setTone(t);if(sel)gen(sel,t);}

  return(
    <div className="page">
      <div className="page-header"><div className="page-eyebrow">📡 Lead Radar</div><h1 className="page-title"><em>Opportunity Feed</em></h1><p className="page-sub">Live athlete legal opportunities · AI personalised outreach · $28M tracked pipeline</p></div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 380px",gap:"1.25rem",alignItems:"start"}}>
        <div>
          <div className="section-label">Live Signals — {LEADS_DATA.length} opportunities</div>
          {LEADS_DATA.map(lead=>(
            <div key={lead.id} className={`lead-card ${lead.urgency} ${sel?.id===lead.id?"sel":""}`} onClick={()=>select(lead)}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:8}}>
                <div><div className="lead-name">{lead.name}</div><div className="lead-sport">{lead.sport}</div></div>
                <div style={{textAlign:"right",flexShrink:0}}>
                  <div className="lead-val">{lead.value}</div>
                  <span className={`tag ${lead.urgency==="urgent"?"tag-red":lead.urgency==="high"?"tag-orange":"tag-yellow"}`} style={{marginTop:4,display:"inline-flex"}}>{lead.urgency}</span>
                </div>
              </div>
              <div className="lead-issue">{lead.issue}</div>
              <div style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1}}>{lead.time} ago · {lead.detail.slice(0,60)}…</div>
            </div>
          ))}
        </div>
        <div>
          <div className="section-label">AI Outreach Generator</div>
          {sel?(
            <div className="outreach-box">
              <div style={{padding:".75rem 1rem",borderBottom:"1px solid var(--border)",display:"flex",alignItems:"center",gap:6,flexWrap:"wrap"}}>
                <span style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1.5,textTransform:"uppercase",flex:1}}>{sel.name}</span>
                {TONES.map(t=><button key={t} className={`tone-btn ${tone===t?"act":""}`} onClick={()=>changeTone(t)}>{t}</button>)}
              </div>
              <div className="outreach-text">{loading?<span style={{color:"var(--text3)",fontFamily:"DM Mono,monospace",fontSize:10}}>GENERATING <Dots/></span>:outreach||"…"}</div>
              <div style={{padding:".75rem 1rem",borderTop:"1px solid var(--border)",display:"flex",gap:8}}>
                <button className="btn btn-gold" onClick={()=>{navigator.clipboard.writeText(outreach);setCopied(true);setTimeout(()=>setCopied(false),2000);}} disabled={!outreach||loading}>{copied?"✓ Copied":"Copy Email"}</button>
                <button className="btn btn-ghost" onClick={()=>gen(sel,tone)} disabled={loading}>↻ Regen</button>
              </div>
            </div>
          ):<div style={{textAlign:"center",padding:"3rem 1rem",color:"var(--text3)",fontFamily:"Cormorant Garamond,serif",fontSize:"1rem",fontStyle:"italic",background:"var(--glass)",border:"1px solid var(--border)",borderRadius:8}}>Select a lead to generate outreach email</div>}
        </div>
      </div>
    </div>
  );
}

// DOCUMENTS
function Documents(){
  const [docType,setDocType]=useState(DOC_TYPES[0]);
  const [party1,setParty1]=useState("");
  const [party2,setParty2]=useState("");
  const [sport,setSport]=useState("Football / Soccer");
  const [details,setDetails]=useState("");
  const [loading,setLoading]=useState(false);
  const [doc,setDoc]=useState("");

  async function generate(){
    if(!party1.trim())return;
    setLoading(true);setDoc("");
    try{
      const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:1000,messages:[{role:"user",content:`Draft a professional ${docType.name} for sports law. Parties: ${party1} and ${party2||"the Club/Brand"}. Sport/League: ${sport}. ${details?"Additional details: "+details:""}. Include all standard clauses with proper legal structure, realistic terms, and placeholder brackets [TERM] where specific values need insertion. Make it professionally formatted and legally realistic.`}]})});
      const d=await r.json();
      setDoc(d.content?.map(b=>b.text||"").join("")||"Generation failed.");
    }catch{setDoc("Connection error. Please try again.");}
    setLoading(false);
  }

  return(
    <div className="page">
      <div className="page-header"><div className="page-eyebrow">📄 Document Generator</div><h1 className="page-title"><em>AI Draft Engine</em></h1><p className="page-sub">40+ document types · All sports · Legally structured · Ready to customise</p></div>
      <div className="section-label">Select Document Type</div>
      <div className="doc-type-grid">
        {DOC_TYPES.map(dt=>(
          <button key={dt.name} className={`doc-type-btn ${docType.name===dt.name?"act":""}`} onClick={()=>setDocType(dt)}>
            <span className="doc-type-icon">{dt.icon}</span>
            <div className="doc-type-name">{dt.name}</div>
            <div className="doc-type-sub">{dt.sub}</div>
          </button>
        ))}
      </div>
      <div className="card" style={{marginBottom:"1rem"}}>
        <div className="card-header"><span className="card-title">Document Details</span></div>
        <div className="card-body">
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:10}}>
            <div><div style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1.5,marginBottom:5}}>PARTY 1 / ATHLETE</div><input className="input" value={party1} onChange={e=>setParty1(e.target.value)} placeholder="e.g. Marcus Johnson"/></div>
            <div><div style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1.5,marginBottom:5}}>PARTY 2 / CLUB / BRAND</div><input className="input" value={party2} onChange={e=>setParty2(e.target.value)} placeholder="e.g. Nike Inc. / Atletico FC"/></div>
            <div><div style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1.5,marginBottom:5}}>SPORT / LEAGUE</div><select className="select" style={{width:"100%"}} value={sport} onChange={e=>setSport(e.target.value)}>{["Football / Soccer","Basketball","NFL","Tennis","Esports","MMA / Boxing","Athletics","Golf"].map(s=><option key={s}>{s}</option>)}</select></div>
            <div><div style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1.5,marginBottom:5}}>KEY DETAILS</div><input className="input" value={details} onChange={e=>setDetails(e.target.value)} placeholder="e.g. 3yr deal, €2M base, La Liga"/></div>
          </div>
          <div style={{display:"flex",gap:8}}>
            <button className="btn btn-gold" onClick={generate} disabled={loading||!party1.trim()}>{loading?<><Dots/> Drafting…</>:`✦ Draft ${docType.name}`}</button>
            {doc&&<button className="btn btn-ghost" onClick={()=>navigator.clipboard.writeText(doc)}>Copy Document</button>}
            {doc&&<button className="btn btn-ghost" onClick={()=>{setDoc("");setParty1("");setParty2("");setDetails("");}}>Clear</button>}
          </div>
        </div>
      </div>
      {doc&&<div className="doc-result">{doc}</div>}
    </div>
  );
}

// CALENDAR
function Calendar(){
  const [selDate,setSelDate]=useState(null);
  const today=new Date(2025,5,5); // June 5 2025
  const [viewMonth,setViewMonth]=useState({y:2025,m:5});
  const daysInMonth=(y,m)=>new Date(y,m+1,0).getDate();
  const firstDay=(y,m)=>new Date(y,m,1).getDay();
  const DAYS=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  const MONTHS=["January","February","March","April","May","June","July","August","September","October","November","December"];

  const cells=[];
  const fd=firstDay(viewMonth.y,viewMonth.m);
  const dim=daysInMonth(viewMonth.y,viewMonth.m);
  const prevDim=daysInMonth(viewMonth.y,viewMonth.m-1);
  for(let i=0;i<fd;i++)cells.push({day:prevDim-fd+i+1,cur:false});
  for(let i=1;i<=dim;i++)cells.push({day:i,cur:true});
  while(cells.length<42)cells.push({day:cells.length-fd-dim+1,cur:false});

  const UPCOMING=[
    {day:2,month:"Jun",title:"CAS Appeal — Yasmin Al-Rashid",sub:"WADA TUE · Anti-Doping",type:"cas",urgent:true},
    {day:5,month:"Jun",title:"NFT Image Rights Hearing",sub:"Marcus Osei / La Liga Club",type:"contract"},
    {day:7,month:"Jun",title:"NFL Franchise Tag Deadline",sub:"Darius Cole / Buffalo Bills",type:"deadline",urgent:true},
    {day:10,month:"Jun",title:"TPO Dispute Filing",sub:"FC Santos Youth Academy",type:"deadline"},
    {day:12,month:"Jun",title:"Esports Non-Compete Hearing",sub:"Aiko Tanaka / LCS",type:"hearing"},
    {day:15,month:"Jun",title:"CAS Appeal — Cole vs NFL",sub:"Arbitration panel constituted",type:"cas"},
    {day:18,month:"Jun",title:"WADA Annual Review",sub:"Global anti-doping compliance",type:"cas"},
    {day:25,month:"Jun",title:"FIFA Training Compensation",sub:"LAFC Academy claim deadline",type:"deadline"},
  ];

  const eventColors={cas:"var(--red)",contract:"var(--blue)",deadline:"var(--orange)",hearing:"var(--purple)"};

  return(
    <div className="page">
      <div className="page-header"><div className="page-eyebrow">📅 Deadline Calendar</div><h1 className="page-title"><em>Case Timeline</em></h1><p className="page-sub">All case deadlines, hearings, and filing dates in one visual overview. Auto-populated from active cases.</p></div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 320px",gap:"1.25rem",alignItems:"start"}}>
        <div>
          <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:"1rem"}}>
            <button className="btn btn-ghost" style={{padding:"5px 12px"}} onClick={()=>setViewMonth(v=>v.m===0?{y:v.y-1,m:11}:{y:v.y,m:v.m-1})}>←</button>
            <span style={{fontFamily:"Cormorant Garamond,serif",fontSize:"1.1rem",color:"var(--text)"}}>{MONTHS[viewMonth.m]} {viewMonth.y}</span>
            <button className="btn btn-ghost" style={{padding:"5px 12px"}} onClick={()=>setViewMonth(v=>v.m===11?{y:v.y+1,m:0}:{y:v.y,m:v.m+1})}>→</button>
          </div>
          <div className="cal-grid">
            {DAYS.map(d=><div key={d} className="cal-day-header">{d}</div>)}
            {cells.map((cell,i)=>{
              const dateKey=`2025-${String(viewMonth.m+1).padStart(2,"0")}-${String(cell.day).padStart(2,"0")}`;
              const events=CAL_EVENTS[dateKey]||[];
              const isToday=cell.cur&&cell.day===5&&viewMonth.m===5&&viewMonth.y===2025;
              return(
                <div key={i} className={`cal-cell ${isToday?"today":""} ${!cell.cur?"other-month":""}`} onClick={()=>setSelDate(cell.cur?dateKey:null)}>
                  <div className={`cal-num ${isToday?"today-num":""}`}>{cell.day}</div>
                  {events.map((ev,j)=><div key={j} className={`cal-event ${ev.type}`}>{ev.title}</div>)}
                </div>
              );
            })}
          </div>
          <div style={{display:"flex",gap:12,flexWrap:"wrap",marginTop:"1rem"}}>
            {[{type:"cas",label:"CAS/Arbitration"},{type:"contract",label:"Contract"},{type:"deadline",label:"Deadline"},{type:"hearing",label:"Hearing"}].map(l=>(
              <div key={l.type} style={{display:"flex",alignItems:"center",gap:6}}>
                <div style={{width:10,height:10,borderRadius:2,background:eventColors[l.type]}}/>
                <span style={{fontFamily:"DM Mono,monospace",fontSize:8,color:"var(--text3)",letterSpacing:1}}>{l.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="card-header"><span className="card-title">Upcoming Events</span><span className={`tag tag-red`}>{UPCOMING.filter(u=>u.urgent).length} Urgent</span></div>
          {UPCOMING.map((u,i)=>(
            <div key={i} className="upcoming-item">
              <div className="up-date"><div className="up-day" style={{color:u.urgent?"var(--red)":"var(--text)"}}>{u.day}</div><div className="up-month">{u.month}</div></div>
              <div><div className="up-title">{u.title}</div><div className="up-sub">{u.sub}</div></div>
              <span className={`tag tag-${u.type==="cas"?"red":u.type==="deadline"?"orange":u.type==="hearing"?"blue":"gold"}`} style={{fontSize:7,whiteSpace:"nowrap"}}>{u.type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// PIPELINE
function Pipeline(){
  const REV=[{val:"$2.1M",lbl:"Active Cases",change:"+12%",up:true},{val:"$840K",lbl:"Invoiced MTD",change:"+8%",up:true},{val:"87%",lbl:"Win Rate",change:"+3%",up:true},{val:"18",lbl:"Open Cases",change:"-2",up:false}];
  return(
    <div className="page">
      <div className="page-header"><div className="page-eyebrow">💰 Revenue Pipeline</div><h1 className="page-title"><em>Case Board & Billing</em></h1><p className="page-sub">Kanban case management · Revenue tracking · Win/loss analytics · Billing forecasts</p></div>
      <div className="revenue-grid">
        {REV.map(r=>(
          <div key={r.lbl} className="rev-stat">
            <div className="rev-stat-val">{r.val}</div>
            <div className="rev-stat-label">{r.lbl}</div>
            <div className="rev-stat-change" style={{color:r.up?"var(--green)":"var(--red)"}}>{r.change} this month</div>
          </div>
        ))}
      </div>
      <div className="section-label">Case Kanban Board</div>
      <div className="kanban">
        {PIPELINE_COLS.map(col=>(
          <div key={col.id} className="kanban-col">
            <div className="kanban-col-header">
              <span className="kanban-col-title" style={{color:col.color}}>{col.title}</span>
              <span className="kanban-count">{col.cases.length}</span>
            </div>
            <div className="kanban-body">
              {col.cases.map((c,i)=>(
                <div key={i} className="kcard">
                  <div className="kcard-name">{c.name}</div>
                  <div className="kcard-type">{c.type}</div>
                  <div className="kcard-val">{c.val}</div>
                  <div className="kcard-due">⏱ {c.due}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// CLIENTS
function Clients(){
  const [selClient,setSelClient]=useState(CLIENTS[0]);
  const [chatInput,setChatInput]=useState("");
  const [messages,setMessages]=useState([{role:"ai",text:`Hello! I'm the AI assistant for LexSport Law Group. I have full context on ${CLIENTS[0].name}'s case. How can I help today?`}]);
  const [chatLoading,setChatLoading]=useState(false);
  const chatRef=useRef();

  useEffect(()=>{
    setMessages([{role:"ai",text:`Hello! I have full context on ${selClient.name}'s cases: ${selClient.cases.join(" and ")}. How can I help you today?`}]);
  },[selClient]);

  useEffect(()=>{if(chatRef.current)chatRef.current.scrollTop=chatRef.current.scrollHeight;},[messages]);

  async function sendChat(){
    if(!chatInput.trim()||chatLoading)return;
    const userMsg=chatInput;setChatInput("");
    setMessages(m=>[...m,{role:"user",text:userMsg}]);
    setChatLoading(true);
    try{
      const history=messages.map(m=>({role:m.role==="ai"?"assistant":"user",content:m.text}));
      const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:600,system:`You are a professional sports law AI assistant at LexSport Law Group. You are assisting with the case of ${selClient.name}, a ${selClient.sport} client with these active cases: ${selClient.cases.join(", ")}. Be helpful, professional, and specific to their situation. Keep responses concise.`,messages:[...history,{role:"user",content:userMsg}]})});
      const d=await r.json();
      const reply=d.content?.map(b=>b.text||"").join("")||"I'm here to help. Could you rephrase that?";
      setMessages(m=>[...m,{role:"ai",text:reply}]);
    }catch{setMessages(m=>[...m,{role:"ai",text:"Connection error. Please try again."}]);}
    setChatLoading(false);
  }

  return(
    <div className="page">
      <div className="page-header"><div className="page-eyebrow">👤 Client Manager</div><h1 className="page-title"><em>Client Intelligence</em></h1><p className="page-sub">Full client profiles · Case history · Document vault · 24/7 AI case assistant</p></div>
      <div className="client-grid">
        <div className="client-list">
          <div style={{padding:".875rem 1rem",borderBottom:"1px solid var(--border)"}}><span style={{fontFamily:"DM Mono,monospace",fontSize:8,letterSpacing:2,color:"var(--text3)",textTransform:"uppercase"}}>Clients · {CLIENTS.length}</span></div>
          {CLIENTS.map(c=>(
            <div key={c.id} className={`client-item ${selClient?.id===c.id?"sel":""}`} onClick={()=>setSelClient(c)}>
              <div className="client-av" style={{background:c.bg,color:c.color}}>{c.flag}</div>
              <div><div className="client-name-small">{c.name}</div><div className="client-sport-small">{c.sport}</div></div>
              <span className={`tag ${c.status==="Urgent"?"tag-red":c.status==="Active"?"tag-green":"tag-gold"}`} style={{marginLeft:"auto",fontSize:7}}>{c.status}</span>
            </div>
          ))}
        </div>
        {selClient&&(
          <div className="client-detail">
            <div className="cd-hero">
              <div className="cd-av-lg" style={{background:selClient.bg,color:selClient.color}}>{selClient.flag}</div>
              <div>
                <div className="cd-name">{selClient.name}</div>
                <div className="cd-sub">{selClient.sport} · {selClient.val} pipeline</div>
                <div style={{marginTop:6,display:"flex",gap:6}}>
                  <span className={`tag ${selClient.status==="Urgent"?"tag-red":selClient.status==="Active"?"tag-green":"tag-gold"}`}>{selClient.status}</span>
                  <span className="tag tag-blue">{selClient.cases.length} Active Cases</span>
                </div>
              </div>
            </div>
            <div className="cd-body">
              <div>
                <div className="cd-section-title">Active Cases</div>
                {selClient.cases.map((c,i)=>(
                  <div key={i} className="case-row">
                    <div className="case-name">{c}</div>
                    <span className="tag tag-blue" style={{fontSize:7}}>Active</span>
                  </div>
                ))}
              </div>
              <div>
                <div className="cd-section-title">AI Case Assistant</div>
                <div style={{background:"var(--bg2)",border:"1px solid var(--border)",borderRadius:8,overflow:"hidden"}}>
                  <div className="chat-messages" ref={chatRef}>
                    {messages.map((m,i)=>(
                      <div key={i} className={`chat-msg ${m.role}`}>
                        <div className={`chat-bubble ${m.role}`}>{m.text}</div>
                      </div>
                    ))}
                    {chatLoading&&<div className="chat-msg"><div className="chat-bubble ai"><Dots/></div></div>}
                  </div>
                  <div className="chat-input-row">
                    <input className="input" style={{fontSize:12}} value={chatInput} onChange={e=>setChatInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&sendChat()} placeholder="Ask about this client's case…"/>
                    <button className="btn btn-gold" style={{padding:"8px 14px"}} onClick={sendChat} disabled={chatLoading||!chatInput.trim()}>→</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const TABS=[
  {id:"home",icon:"🏠",label:"Dashboard"},
  {id:"contracts",icon:"⚖️",label:"Contracts"},
  {id:"research",icon:"🔍",label:"Research"},
  {id:"leads",icon:"📡",label:"Leads",badge:"2"},
  {id:"documents",icon:"📄",label:"Documents"},
  {id:"calendar",icon:"📅",label:"Calendar"},
  {id:"pipeline",icon:"💰",label:"Pipeline"},
  {id:"clients",icon:"👤",label:"Clients"},
];

const VIEWS={home:Home,contracts:Contracts,research:Research,leads:Leads,documents:Documents,calendar:Calendar,pipeline:Pipeline,clients:Clients};

export default function LexSportComplete(){
  const [view,setView]=useState("home");
  const View=VIEWS[view]||Home;
  return(
    <>
      <style>{CSS}</style>
      <div className="app">
        <div className="bg-mesh"><div className="orb orb1"/><div className="orb orb2"/><div className="orb orb3"/></div>
        <div className="bg-grid"/>
        <nav className="nav">
          <div className="logo"><div className="logo-dot"/>Lex<em>Sport</em></div>
          <div className="nav-tabs">
            {TABS.map(t=>(
              <button key={t.id} className={`ntab ${view===t.id?"active":""}`} onClick={()=>setView(t.id)}>
                <span>{t.icon}</span><span>{t.label}</span>
                {t.badge&&<span className="nbadge">{t.badge}</span>}
              </button>
            ))}
          </div>
          <div className="nav-r"><Clock/><div className="nav-av">SL</div></div>
        </nav>
        <div style={{position:"relative",zIndex:1}}><View onNav={setView}/></div>
      </div>
    </>
  );
}
