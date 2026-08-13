"""True Surviving SMP landing page."""

import json
import os
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
LOGO_PATH = PROJECT_DIR / "images" / "server-icon.png"

st.set_page_config(
    page_title="True Surviving SMP",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "T",
    layout="centered",
    initial_sidebar_state="collapsed",
)


ROLE_QUESTIONS = {
    "Moderator": {
        "level": "EASY STARTER ASSESSMENT",
        "description": "This checks friendly, fair, everyday moderation decisions.",
        "questions": (
            (
                "A player is repeatedly spamming chat after one polite reminder. What should you do next?",
                (
                    "Issue the appropriate warning, keep chat calm, and document the action.",
                    "Mute everyone in chat immediately.",
                    "Ignore it because they may stop later.",
                ),
            ),
            (
                "A player reports that their base was griefed. What is your best first step?",
                (
                    "Gather the available evidence and investigate before taking action.",
                    "Ban the closest player to the base immediately.",
                    "Tell the player there is nothing staff can do.",
                ),
            ),
            (
                "A new player accidentally breaks a simple server rule. How should you respond?",
                (
                    "Explain the rule clearly and apply the fair action if one is needed.",
                    "Publicly shame them so everyone learns.",
                    "Give them a permanent ban without checking context.",
                ),
            ),
        ),
    },
    "Administrator": {
        "level": "MEDIUM ADMINISTRATOR ASSESSMENT",
        "description": "This checks evidence handling, escalation, and consistent decisions.",
        "questions": (
            (
                "A banned player appeals and says the evidence is wrong. What is the best response?",
                (
                    "Review logs and evidence objectively, then decide using the server policy.",
                    "Reject every appeal to avoid extra work.",
                    "Remove the ban instantly without checking anything.",
                ),
            ),
            (
                "You find a player using a possible exploit. What should happen first?",
                (
                    "Contain the impact, preserve evidence, and alert senior staff promptly.",
                    "Post the exploit details in public chat.",
                    "Use the exploit yourself to see how far it goes.",
                ),
            ),
            (
                "Two staff members disagree about a punishment. What is the fair approach?",
                (
                    "Compare the evidence and policy, then escalate if an impartial decision is needed.",
                    "Always side with the highest rank without checking details.",
                    "Punish the player twice so both staff members are satisfied.",
                ),
            ),
        ),
    },
    "Sulfur (Administrator)": {
        "level": "HARD SULFUR ASSESSMENT",
        "description": "This checks high-trust judgment for incidents that affect the whole server.",
        "questions": (
            (
                "A duplication exploit is spreading quickly. What is the strongest first response?",
                (
                    "Limit the damage, preserve evidence, and coordinate a confidential response with leadership.",
                    "Announce every exploit step publicly so everyone knows it.",
                    "Wait until the next day in case the problem fixes itself.",
                ),
            ),
            (
                "You notice inconsistent punishments for similar rule breaks. What should you do?",
                (
                    "Audit the cases, identify the pattern, and propose a consistent staff process.",
                    "Keep the inconsistency secret because it is already done.",
                    "Give all future players the harshest possible punishment.",
                ),
            ),
            (
                "A new plugin update may delete player data. What is the safest decision?",
                (
                    "Pause the rollout, verify backups, and test with the technical team before release.",
                    "Deploy it during peak hours and hope for the best.",
                    "Delete old backups to make space first.",
                ),
            ),
        ),
    },
    "CEO": {
        "level": "INTERMEDIATE CEO ASSESSMENT",
        "description": "This checks calm leadership, communication, and healthy community decisions.",
        "questions": (
            (
                "Players are upset about a major change. How should you lead the response?",
                (
                    "Acknowledge feedback, explain the reason clearly, and share a realistic review plan.",
                    "Mute all criticism and never explain the change.",
                    "Promise every requested change immediately.",
                ),
            ),
            (
                "Your staff team is missing shifts and communication is unclear. What should you do?",
                (
                    "Set clear expectations, a simple schedule, and regular check-ins with the team.",
                    "Remove every staff member without speaking to them.",
                    "Let the problem continue until someone else fixes it.",
                ),
            ),
            (
                "You are planning a new store perk. What must guide the decision?",
                (
                    "Keep it EULA-compliant, non-pay-to-win, and clearly communicated to players.",
                    "Make it the strongest gameplay advantage possible.",
                    "Hide the perk details until after players buy it.",
                ),
            ),
        ),
    },
}


def page_style() -> None:
    """Apply presentation-only styling to Streamlit's built-in components."""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #050706;
            background-image:
                radial-gradient(circle at 50% -12%, rgba(67, 255, 126, 0.21), transparent 31rem),
                radial-gradient(circle at 8% 92%, rgba(27, 139, 66, 0.13), transparent 26rem),
                repeating-linear-gradient(0deg, transparent 0, transparent 5px, rgba(255,255,255,0.018) 6px);
            color: #ffffff;
        }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container {
            max-width: 960px;
            padding-top: 2.8rem;
            padding-bottom: 4.5rem;
        }
        [data-testid="stImage"] img {
            background: #0a0e0b;
            border: 1px solid rgba(131, 255, 164, 0.42);
            border-radius: 20px;
            padding: 7px;
            box-shadow: 0 0 0 6px rgba(56, 225, 106, 0.07), 0 20px 46px rgba(0, 0, 0, 0.62);
        }
        /* Hide Streamlit's expand/fullscreen control on the server logo. */
        [data-testid="stImage"] button {
            display: none !important;
        }
        .brand-lockup {
            margin: 1.15rem 0 2.35rem;
            text-align: center;
            user-select: none;
        }
        .brand-lockup::after {
            content: "";
            display: block;
            width: 82px;
            height: 2px;
            margin: 1rem auto 0;
            background: linear-gradient(90deg, transparent, #63ff95, transparent);
        }
        .brand-name {
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: clamp(1.5rem, 4vw, 1.85rem);
            font-weight: 900;
            letter-spacing: 0.045em;
            line-height: 1.1;
            text-shadow: 0 0 20px rgba(100, 255, 147, 0.15);
        }
        .brand-tagline {
            color: #b9cdbd;
            font-size: 0.9rem;
            font-weight: 600;
            letter-spacing: 0.13em;
            margin-top: 0.48rem;
            text-transform: uppercase;
        }
        .home-console {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 0.52rem;
            margin: 1.05rem 0 -0.55rem;
            user-select: none;
        }
        .console-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            min-height: 29px;
            padding: 0.34rem 0.56rem;
            border: 1px solid rgba(124, 246, 158, 0.25);
            border-radius: 7px;
            background: rgba(12, 27, 16, 0.77);
            color: #c3f5ce;
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }
        .console-chip.code { color: #afffc7; }
        .console-chip.online { border-color: rgba(122, 255, 157, 0.38); color: #e1ffea; }
        .live-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #62f18d;
            box-shadow: 0 0 9px rgba(98, 241, 141, 0.85);
        }
        .mc-blocks {
            display: inline-flex;
            gap: 3px;
            padding: 4px;
            border: 1px solid rgba(121, 244, 155, 0.18);
            border-radius: 7px;
            background: rgba(4, 8, 5, 0.65);
        }
        .mc-block {
            display: block;
            width: 18px;
            height: 18px;
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 2px;
            image-rendering: pixelated;
            box-shadow: inset 3px 3px 0 rgba(255,255,255,0.11), inset -3px -3px 0 rgba(0,0,0,0.22);
        }
        .mc-block.grass { background: linear-gradient(#5ddb57 0 27%, #734f2e 27% 100%); }
        .mc-block.stone { background: linear-gradient(135deg, #9aa4a0 25%, #78837f 25% 50%, #9da7a3 50% 75%, #727d79 75%); background-size: 8px 8px; }
        .mc-block.ore { background: #697672; box-shadow: inset 3px 3px 0 rgba(255,255,255,0.13), inset -3px -3px 0 rgba(0,0,0,0.2), 5px 4px 0 -3px #48f59b, -3px -4px 0 -3px #48f59b; }
        .rules-hero {
            position: relative;
            overflow: hidden;
            padding: 2rem 1.65rem 1.75rem;
            margin: 0 0 1.3rem;
            border: 1px solid rgba(110, 255, 151, 0.38);
            border-left: 5px solid #63ed91;
            border-radius: 15px;
            background:
                linear-gradient(115deg, rgba(43, 173, 83, 0.30) 0%, rgba(16, 29, 19, 0.86) 42%, rgba(5, 7, 6, 0.94) 100%);
            box-shadow: 0 18px 42px rgba(0,0,0,0.36), inset 0 1px 0 rgba(255,255,255,0.1);
        }
        .rules-hero::after {
            content: "";
            position: absolute;
            width: 190px;
            height: 190px;
            right: -60px;
            top: -105px;
            border: 1px solid rgba(118, 255, 157, 0.18);
            border-radius: 50%;
            box-shadow: 0 0 0 28px rgba(118, 255, 157, 0.035), 0 0 0 57px rgba(118, 255, 157, 0.025);
        }
        .rules-kicker {
            position: relative;
            z-index: 1;
            color: #84f6a8;
            font-size: 0.73rem;
            font-weight: 900;
            letter-spacing: 0.16em;
        }
        .rules-title {
            position: relative;
            z-index: 1;
            margin-top: 0.32rem;
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: clamp(1.85rem, 6vw, 2.8rem);
            font-weight: 900;
            letter-spacing: 0.035em;
            line-height: 1;
        }
        .rules-intro {
            position: relative;
            z-index: 1;
            max-width: 570px;
            margin: 0.9rem 0 0;
            color: #cfdbd1;
            font-size: 1rem;
            line-height: 1.65;
        }
        .rules-warning {
            position: relative;
            z-index: 1;
            display: inline-block;
            margin-top: 1.15rem;
            padding: 0.46rem 0.7rem;
            border: 1px solid rgba(255, 193, 98, 0.32);
            border-radius: 999px;
            background: rgba(112, 67, 16, 0.30);
            color: #ffe1a9;
            font-size: 0.81rem;
            font-weight: 700;
        }
        .rules-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1.2rem;
        }
        .rule-card {
            min-height: 253px;
            overflow: hidden;
            border: 1px solid rgba(124, 222, 151, 0.25);
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(30, 73, 42, 0.56), rgba(8, 12, 10, 0.96) 53%);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 11px 25px rgba(0,0,0,0.25);
        }
        .rule-card-head {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 1rem 1.05rem 0.8rem;
            border-bottom: 1px solid rgba(126, 255, 163, 0.17);
            background: linear-gradient(100deg, rgba(35, 170, 76, 0.33), rgba(23, 41, 27, 0.08));
        }
        .rule-card-number {
            display: grid;
            place-items: center;
            flex: 0 0 auto;
            width: 28px;
            height: 28px;
            border-radius: 8px;
            background: #71ef9a;
            color: #082110;
            font-size: 0.82rem;
            font-weight: 900;
        }
        .rule-card-title {
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: 1rem;
            font-weight: 900;
            letter-spacing: 0.08em;
        }
        .rule-list {
            margin: 0;
            padding: 0.9rem 1.05rem 1rem;
            list-style: none;
        }
        .rule-list li {
            position: relative;
            padding: 0 0 0.86rem 1.05rem;
            color: #b9cabc;
            font-size: 0.91rem;
            line-height: 1.42;
        }
        .rule-list li:last-child { padding-bottom: 0; }
        .rule-list li::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0.48rem;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #70f49c;
            box-shadow: 0 0 9px rgba(112, 244, 156, 0.55);
        }
        .rule-list strong { color: #f4fff6; }
        .rules-footer {
            margin: 0 0 1rem;
            padding: 0.85rem 1rem;
            border: 1px solid rgba(102, 232, 137, 0.22);
            border-radius: 11px;
            background: rgba(24, 96, 47, 0.19);
            color: #b9d8c0;
            font-size: 0.9rem;
            text-align: center;
        }
        .terms-hero {
            position: relative;
            overflow: hidden;
            padding: 2.15rem 1.7rem 1.8rem;
            margin: 0 0 1.2rem;
            border: 1px solid rgba(117, 246, 151, 0.4);
            border-bottom: 4px solid #39bd62;
            border-radius: 15px;
            background: linear-gradient(120deg, rgba(45, 176, 83, 0.37), rgba(16, 28, 18, 0.94) 48%, #070907 100%);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.13), 0 20px 48px rgba(0,0,0,0.40);
        }
        .terms-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            opacity: 0.34;
            background: repeating-linear-gradient(135deg, transparent 0, transparent 16px, rgba(117, 255, 155, 0.055) 16px, rgba(117, 255, 155, 0.055) 17px);
            pointer-events: none;
        }
        .terms-kicker, .terms-title, .terms-copy { position: relative; z-index: 1; }
        .terms-kicker {
            color: #8affae;
            font-size: 0.73rem;
            font-weight: 900;
            letter-spacing: 0.17em;
        }
        .terms-title {
            margin-top: 0.34rem;
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: clamp(1.85rem, 6vw, 2.8rem);
            font-weight: 900;
            letter-spacing: 0.035em;
            line-height: 1;
            text-shadow: 0 0 25px rgba(111, 255, 151, 0.16);
        }
        .terms-copy {
            max-width: 630px;
            margin: 0.85rem 0 0;
            color: #cad8cc;
            font-size: 0.98rem;
            line-height: 1.6;
        }
        .terms-stack { display: grid; gap: 0.88rem; }
        .term-card {
            position: relative;
            overflow: hidden;
            padding: 1.15rem 1.25rem 1.22rem 5rem;
            border: 1px solid rgba(113, 236, 146, 0.25);
            border-radius: 13px;
            background: linear-gradient(105deg, rgba(30, 119, 56, 0.22), rgba(9, 14, 10, 0.98) 32%);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 10px 25px rgba(0,0,0,0.25);
        }
        .term-card::before {
            content: attr(data-section);
            position: absolute;
            left: 1.15rem;
            top: 0.62rem;
            color: rgba(117, 255, 156, 0.23);
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: 3.1rem;
            font-weight: 900;
            line-height: 1;
        }
        .term-card::after {
            content: "";
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            width: 3px;
            background: linear-gradient(#8affad, #228344);
        }
        .term-heading {
            color: #f8fffa;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: 1rem;
            font-weight: 900;
            letter-spacing: 0.065em;
            line-height: 1.3;
        }
        .term-text {
            margin: 0.58rem 0 0;
            color: #c0d0c3;
            font-size: 0.93rem;
            line-height: 1.63;
        }
        .term-points {
            margin: 0.66rem 0 0;
            padding: 0;
            list-style: none;
        }
        .term-points li {
            position: relative;
            margin-top: 0.46rem;
            padding-left: 1rem;
            color: #c6d5c8;
            font-size: 0.91rem;
            line-height: 1.48;
        }
        .term-points li::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0.44rem;
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #79f6a0;
            box-shadow: 0 0 8px rgba(121,246,160,0.5);
        }
        .terms-agreement {
            margin: 1rem 0;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(122, 239, 153, 0.25);
            border-radius: 11px;
            background: rgba(29, 112, 53, 0.18);
            color: #cbe7d0;
            font-size: 0.9rem;
            line-height: 1.5;
            text-align: center;
        }
        .staff-hero {
            position: relative;
            overflow: hidden;
            padding: 2.1rem 1.7rem 1.85rem;
            margin: 0 0 1.2rem;
            border: 1px solid rgba(124, 247, 159, 0.40);
            border-radius: 15px;
            background: linear-gradient(120deg, rgba(34, 151, 70, 0.41), rgba(13, 25, 15, 0.94) 48%, #070907 100%);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.13), 0 20px 48px rgba(0,0,0,0.40);
        }
        .staff-hero::after {
            content: "";
            position: absolute;
            width: 220px;
            height: 220px;
            right: -80px;
            top: -115px;
            border: 1px solid rgba(124, 255, 160, 0.20);
            border-radius: 50%;
            box-shadow: 0 0 0 23px rgba(97, 243, 139, 0.035), 0 0 0 49px rgba(97, 243, 139, 0.025);
        }
        .staff-kicker, .staff-title, .staff-copy { position: relative; z-index: 1; }
        .staff-kicker {
            color: #89f9ac;
            font-size: 0.73rem;
            font-weight: 900;
            letter-spacing: 0.17em;
        }
        .staff-title {
            margin-top: 0.36rem;
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: clamp(1.85rem, 6vw, 2.8rem);
            font-weight: 900;
            letter-spacing: 0.035em;
            line-height: 1;
            text-shadow: 0 0 25px rgba(111, 255, 151, 0.16);
        }
        .staff-copy {
            max-width: 630px;
            margin: 0.85rem 0 0;
            color: #cbd8ce;
            font-size: 0.98rem;
            line-height: 1.6;
        }
        .staff-status {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            position: relative;
            z-index: 1;
            margin-top: 1.1rem;
        }
        .staff-status span {
            padding: 0.35rem 0.58rem;
            border: 1px solid rgba(122, 255, 158, 0.25);
            border-radius: 999px;
            background: rgba(20, 87, 42, 0.32);
            color: #bfffd1;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
        }
        .staff-section-label {
            margin: 1.25rem 0 0.45rem;
            color: #92f9b3;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.13em;
        }
        .staff-role-note {
            margin: 0.75rem 0 1rem;
            padding: 0.82rem 0.95rem;
            border: 1px solid rgba(112, 236, 146, 0.22);
            border-radius: 11px;
            background: linear-gradient(90deg, rgba(34, 132, 62, 0.22), rgba(8, 12, 9, 0.58));
            color: #c5d9c9;
            font-size: 0.88rem;
            line-height: 1.48;
        }
        .staff-role-note strong { color: #fbfffc; }
        .staff-question-card {
            margin: 0.9rem 0 0;
            padding: 1.1rem 1.15rem 0.2rem;
            border: 1px solid rgba(111, 236, 146, 0.26);
            border-radius: 13px;
            background: linear-gradient(115deg, rgba(28, 104, 50, 0.24), rgba(7, 11, 8, 0.98) 35%);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 10px 24px rgba(0,0,0,0.22);
        }
        .staff-question-heading {
            color: #f4fff6;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: 0.92rem;
            font-weight: 900;
            letter-spacing: 0.05em;
        }
        [data-testid="stTextInput"] input, [data-testid="stDateInput"] input,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border-color: rgba(111, 236, 146, 0.34) !important;
            background-color: #0b110d !important;
            color: #f7fff8 !important;
            box-shadow: none !important;
        }
        [data-testid="stTextInput"] label, [data-testid="stDateInput"] label,
        [data-testid="stSelectbox"] label, [data-testid="stRadio"] label,
        [data-testid="stCheckbox"] label { color: #e7f4e9 !important; font-weight: 700 !important; }
        [data-testid="stRadio"] { padding: 0.4rem 0 0.65rem; }
        [data-testid="stRadio"] [role="radiogroup"] { gap: 0.32rem; }
        [data-testid="stRadio"] [role="radiogroup"] > label {
            margin: 0 !important;
            padding: 0.58rem 0.7rem !important;
            border: 1px solid rgba(111, 236, 146, 0.24);
            border-radius: 8px;
            background: rgba(28, 72, 40, 0.56);
            transition: background 150ms ease, border-color 150ms ease, transform 150ms ease;
        }
        [data-testid="stRadio"] [role="radiogroup"] > label:hover {
            border-color: #82f7a9;
            background: rgba(41, 130, 64, 0.62);
            transform: translateX(3px);
        }
        [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
            border-color: #a1ffc0;
            background: linear-gradient(100deg, rgba(50, 182, 87, 0.75), rgba(25, 85, 43, 0.78));
            box-shadow: 0 0 15px rgba(78, 235, 119, 0.16);
        }
        [data-testid="stRadio"] [role="radiogroup"] > label,
        [data-testid="stRadio"] [role="radiogroup"] > label p,
        [data-testid="stRadio"] [role="radiogroup"] > label span {
            color: #e6ffeb !important;
            opacity: 1 !important;
        }
        [data-testid="stRadio"] [role="radio"] { background-color: #0b110d !important; border-color: #8cf5ad !important; }
        .staff-privacy {
            margin: 1rem 0 0.3rem;
            color: #a9c5ae;
            font-size: 0.82rem;
            line-height: 1.45;
        }
        .punishment-hero {
            position: relative;
            overflow: hidden;
            padding: 2.1rem 1.7rem 1.85rem;
            margin: 0 0 1.2rem;
            border: 1px solid rgba(248, 177, 99, 0.40);
            border-radius: 15px;
            background: linear-gradient(120deg, rgba(159, 82, 32, 0.39), rgba(37, 24, 15, 0.94) 48%, #090807 100%);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.10), 0 20px 48px rgba(0,0,0,0.40);
        }
        .punishment-hero::after {
            content: "";
            position: absolute;
            width: 230px;
            height: 230px;
            right: -88px;
            top: -118px;
            border: 1px solid rgba(255, 188, 105, 0.20);
            border-radius: 50%;
            box-shadow: 0 0 0 23px rgba(255, 175, 85, 0.035), 0 0 0 49px rgba(255, 175, 85, 0.025);
        }
        .punishment-kicker, .punishment-title, .punishment-copy { position: relative; z-index: 1; }
        .punishment-kicker {
            color: #ffd28f;
            font-size: 0.73rem;
            font-weight: 900;
            letter-spacing: 0.17em;
        }
        .punishment-title {
            margin-top: 0.36rem;
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: clamp(1.8rem, 6vw, 2.72rem);
            font-weight: 900;
            letter-spacing: 0.035em;
            line-height: 1;
            text-shadow: 0 0 25px rgba(255, 175, 85, 0.13);
        }
        .punishment-copy {
            max-width: 600px;
            margin: 0.85rem 0 0;
            color: #e0cdc0;
            font-size: 0.98rem;
            line-height: 1.6;
        }
        .punishment-ladder {
            display: grid;
            gap: 0.8rem;
            margin: 0 0 1.1rem;
        }
        .punishment-card {
            position: relative;
            display: grid;
            grid-template-columns: 76px minmax(0, 1fr) auto;
            align-items: center;
            gap: 1rem;
            overflow: hidden;
            min-height: 96px;
            padding: 1rem 1.25rem 1rem 1rem;
            border: 1px solid rgba(240, 196, 135, 0.25);
            border-radius: 13px;
            background: linear-gradient(105deg, rgba(88, 58, 26, 0.32), rgba(10, 12, 9, 0.98) 41%);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 10px 25px rgba(0,0,0,0.25);
        }
        .punishment-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: #8ae5a2;
        }
        .punishment-card.level-2::before { background: #ffe081; }
        .punishment-card.level-3::before { background: #ffb25f; }
        .punishment-card.level-4::before { background: #ff765f; }
        .punishment-card.level-5::before { background: #ff4f57; }
        .punishment-stage {
            display: grid;
            place-items: center;
            width: 60px;
            height: 60px;
            border: 1px solid rgba(155, 248, 181, 0.34);
            border-radius: 12px;
            background: rgba(44, 134, 65, 0.32);
            color: #afffc5;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: 1.35rem;
            font-weight: 900;
            letter-spacing: 0.04em;
        }
        .level-2 .punishment-stage { border-color: rgba(255, 224, 129, 0.38); background: rgba(132, 102, 31, 0.30); color: #ffe6a6; }
        .level-3 .punishment-stage { border-color: rgba(255, 178, 95, 0.40); background: rgba(138, 74, 25, 0.31); color: #ffd0a0; }
        .level-4 .punishment-stage { border-color: rgba(255, 118, 95, 0.42); background: rgba(130, 47, 29, 0.33); color: #ffc1b2; }
        .level-5 .punishment-stage { border-color: rgba(255, 79, 87, 0.50); background: rgba(132, 32, 39, 0.35); color: #ffc1c4; }
        .punishment-label {
            color: #d4e2d6;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }
        .punishment-action {
            margin-top: 0.24rem;
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: clamp(1.05rem, 3.4vw, 1.28rem);
            font-weight: 900;
            line-height: 1.22;
        }
        .punishment-badge {
            padding: 0.45rem 0.6rem;
            border: 1px solid rgba(165, 255, 190, 0.25);
            border-radius: 999px;
            background: rgba(47, 146, 71, 0.18);
            color: #bcffce;
            font-size: 0.68rem;
            font-weight: 900;
            letter-spacing: 0.09em;
            white-space: nowrap;
        }
        .level-2 .punishment-badge { border-color: rgba(255, 225, 129, 0.28); background: rgba(130, 98, 25, 0.18); color: #ffe5a2; }
        .level-3 .punishment-badge { border-color: rgba(255, 178, 95, 0.29); background: rgba(140, 76, 25, 0.18); color: #ffd0a0; }
        .level-4 .punishment-badge { border-color: rgba(255, 118, 95, 0.32); background: rgba(139, 46, 29, 0.20); color: #ffc1b2; }
        .level-5 .punishment-badge { border-color: rgba(255, 79, 87, 0.36); background: rgba(139, 28, 38, 0.24); color: #ffc1c4; }
        .punishment-footer {
            margin: 0 0 1rem;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(250, 191, 109, 0.25);
            border-radius: 11px;
            background: rgba(119, 66, 25, 0.17);
            color: #f0d9bb;
            font-size: 0.9rem;
            line-height: 1.48;
            text-align: center;
        }
        [data-testid="stButton"] {
            margin-bottom: 1rem;
        }
        [data-testid="stButton"] > button {
            position: relative;
            min-height: 84px;
            width: 100%;
            overflow: hidden;
            border: 1px solid rgba(112, 255, 152, 0.55);
            border-left: 4px solid #78ffa3;
            border-radius: 12px;
            background: linear-gradient(118deg, #2bad53 0%, #197b3a 39.5%, #101711 40%, #050706 100%);
            color: #ffffff;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            font-size: 1.08rem;
            font-weight: 800;
            letter-spacing: 0.035em;
            text-align: left;
            padding: 0 5rem 0 1.45rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.16), inset 0 -1px 0 rgba(0,0,0,0.5), 0 10px 26px rgba(0,0,0,0.3);
            transition: transform 170ms ease, border-color 170ms ease, box-shadow 170ms ease, filter 170ms ease;
            user-select: none;
        }
        [data-testid="stButton"] > button p { font-size: inherit; }
        [data-testid="stButton"] > button::after {
            content: "→";
            position: absolute;
            right: 1.45rem;
            top: 50%;
            transform: translateY(-52%);
            color: #92ffb6;
            font-size: 2.15rem;
            font-weight: 700;
            line-height: 1;
            text-shadow: 0 0 14px rgba(104, 255, 148, 0.45);
        }
        [data-testid="stButton"] > button:hover {
            transform: translateY(-3px) scale(1.008);
            border-color: #baffce;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 0 0 1px rgba(123, 255, 162, 0.18), 0 16px 30px rgba(0,0,0,0.42), 0 0 28px rgba(55, 224, 105, 0.13);
            filter: brightness(1.12);
        }
        [data-testid="stButton"] > button:active {
            transform: translateY(0) scale(0.995);
        }
        [data-testid="stButton"] > button:focus-visible {
            outline: 3px solid #d8ffe2;
            outline-offset: 3px;
        }
        @media (max-width: 640px) {
            .block-container { padding: 2.2rem 1.1rem 3rem; }
            [data-testid="stButton"] > button { min-height: 74px; font-size: 0.98rem; }
            .rules-hero { padding: 1.55rem 1.2rem 1.4rem; }
            .rules-grid { grid-template-columns: 1fr; }
            .rule-card { min-height: 0; }
            .terms-hero { padding: 1.55rem 1.2rem 1.4rem; }
            .term-card { padding: 1.05rem 1rem 1.1rem 4.25rem; }
            .term-card::before { left: 0.95rem; font-size: 2.7rem; }
            .staff-hero { padding: 1.55rem 1.2rem 1.4rem; }
            .staff-question-card { padding: 1rem 0.9rem 0.15rem; }
            .punishment-hero { padding: 1.55rem 1.2rem 1.4rem; }
            .punishment-card { grid-template-columns: 55px minmax(0, 1fr); gap: 0.75rem; padding: 0.82rem 0.85rem; }
            .punishment-stage { width: 48px; height: 48px; border-radius: 10px; font-size: 1.06rem; }
            .punishment-badge { display: none; }
            .home-console { margin-top: 0.9rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_logo() -> None:
    """Render the project logo, without failing if the file has not been added yet."""
    logo_column = st.columns([1, 1.15, 1])[1]
    with logo_column:
        if LOGO_PATH.is_file():
            st.image(str(LOGO_PATH), use_container_width=True)
        else:
            st.markdown("<div style='text-align:center; font-size:4rem;'>⛏️</div>", unsafe_allow_html=True)


def show_rules() -> None:
    """Display the server rules in a player-friendly format."""
    st.markdown(
        """
        <section class="rules-hero">
          <div class="rules-kicker">&#128220; TRUE SURVIVING SMP</div>
          <div class="rules-title">SERVER RULES</div>
          <p class="rules-intro">Welcome to the server! Keep it fair, keep it clean.</p>
          <div class="rules-warning">Breaking these rules will result in a kick or ban.</div>
        </section>

        <section class="rules-grid">
          <article class="rule-card">
            <div class="rule-card-head"><span class="rule-card-number">1</span><span class="rule-card-title">&#128721; GAMEPLAY</span></div>
            <ul class="rule-list">
              <li><strong>No Griefing</strong> &ndash; Do not destroy other players' builds or community areas.</li>
              <li><strong>No Stealing</strong> &ndash; Do not take items from chests or farms without permission.</li>
              <li><strong>No Cheating</strong> &ndash; Hacked clients, X-ray packs, and item duping are permanently banned.</li>
            </ul>
          </article>

          <article class="rule-card">
            <div class="rule-card-head"><span class="rule-card-number">2</span><span class="rule-card-title">&#128172; CHAT</span></div>
            <ul class="rule-list">
              <li><strong>Be Respectful</strong> &ndash; Toxicity, harassment, and hate speech are strictly prohibited.</li>
              <li><strong>No Advertising</strong> &ndash; Do not promo other servers or links in chat or DMs.</li>
              <li><strong>No Spam</strong> &ndash; Keep chat clean and clear of repetitive text or links.</li>
            </ul>
          </article>

          <article class="rule-card">
            <div class="rule-card-head"><span class="rule-card-number">3</span><span class="rule-card-title">&#128205; BUILDING</span></div>
            <ul class="rule-list">
              <li><strong>Give Space</strong> &ndash; Do not build within 150 blocks of another player's base.</li>
              <li><strong>Clean Up</strong> &ndash; Chop trees down fully and remove random 1x1 towers.</li>
            </ul>
          </article>

          <article class="rule-card">
            <div class="rule-card-head"><span class="rule-card-number">4</span><span class="rule-card-title">&#128736; SERVER HEALTH</span></div>
            <ul class="rule-list">
              <li><strong>No Lag Machines</strong> &ndash; Do not build intentionally laggy automated systems.</li>
              <li><strong>Report Bugs</strong> &ndash; Open a support ticket immediately if you find an exploit.</li>
            </ul>
          </article>
        </section>

        <div class="rules-footer">Play fair. Build smart. Make the SMP better for everyone.</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Back to main menu", key="back-to-menu", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()


def show_terms() -> None:
    """Display the server terms in a clear, official layout."""
    st.markdown(
        """
        <section class="terms-hero">
          <div class="terms-kicker">&#128737; TRUE SURVIVING SMP &bull; PLAYER AGREEMENT</div>
          <div class="terms-title">TERMS OF SERVICE</div>
          <p class="terms-copy">The agreement that keeps our website, Discord, and Minecraft server fair, safe, and enjoyable for everyone.</p>
        </section>

        <section class="terms-stack">
          <article class="term-card" data-section="01">
            <div class="term-heading">ACCEPTANCE OF TERMS</div>
            <p class="term-text">By accessing this website or connecting to our Minecraft server (the &quot;Service&quot;), you agree to be bound by these Terms of Service, all applicable laws, and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing this site or the server.</p>
          </article>

          <article class="term-card" data-section="02">
            <div class="term-heading">MOJANG DISCLAIMER &amp; COMPLIANCE</div>
            <p class="term-text">Our Service is an independent Minecraft multiplayer network. We are NOT affiliated with, endorsed by, or associated with Mojang Studios, Microsoft, or any of their official partners.</p>
            <p class="term-text">All virtual items, perks, ranks, and cosmetics sold on our store strictly comply with the Minecraft End User License Agreement (EULA) and Mojang&rsquo;s Commercial Usage Guidelines. Purchases are made as voluntary contributions to keep the server online and do not provide gameplay-breaking or pay-to-win advantages.</p>
          </article>

          <article class="term-card" data-section="03">
            <div class="term-heading">VIRTUAL GOODS &amp; REFUND POLICY</div>
            <p class="term-text">All transactions made on our webstore are final. Payments are processed voluntarily in exchange for virtual, non-tangible goods used within the Service.</p>
            <ul class="term-points">
              <li><strong>No Refunds:</strong> Under no circumstances will refunds be issued for virtual goods, ranks, or currency.</li>
              <li><strong>Chargebacks:</strong> Initiating a dispute or chargeback with a payment processor (such as PayPal or a credit card company) without prior written consent from server administration will result in an immediate, permanent, and unappealable ban from the network, including our website, Discord, and Minecraft server.</li>
            </ul>
          </article>

          <article class="term-card" data-section="04">
            <div class="term-heading">USER CONDUCT &amp; SERVER RULES</div>
            <p class="term-text">You agree to use our website and server only for lawful purposes. You are strictly prohibited from:</p>
            <ul class="term-points">
              <li>Utilizing hacked clients, unauthorized mods, X-ray packs, or macro exploits.</li>
              <li>Engaging in toxic behavior, hate speech, severe harassment, or doxxing.</li>
              <li>Advertising other Minecraft servers or external commercial links.</li>
              <li>Intentionally degrading server performance, crashing instances, or exploiting bugs.</li>
            </ul>
          </article>

          <article class="term-card" data-section="05">
            <div class="term-heading">TERMINATION OF ACCESS</div>
            <p class="term-text">The server administration reserves the right to terminate, suspend, or restrict your access to the website, Discord, or Minecraft server at any time, for any reason, and without prior notice or refund. If you break the server rules and are banned, you forfeit access to any virtual goods or ranks purchased on your account.</p>
          </article>

          <article class="term-card" data-section="06">
            <div class="term-heading">LIMITATION OF LIABILITY</div>
            <p class="term-text">The Service, its website, and all related content are provided on an &quot;as-is&quot; and &quot;as-available&quot; basis. We make no warranties, expressed or implied, regarding server uptime, performance, or data stability. We are not liable for any lost in-game items, data corruption, world wipes, or account security breaches.</p>
          </article>

          <article class="term-card" data-section="07">
            <div class="term-heading">CHANGES TO TERMS</div>
            <p class="term-text">We reserve the right to revise or update these Terms of Service at any time without prior notice. By continuing to use the website or server, you agree to be bound by the current version of these terms.</p>
          </article>
        </section>

        <div class="terms-agreement">By continuing to use True Surviving SMP, you confirm that you understand and accept these Terms of Service.</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Back to main menu", key="terms-back-to-menu", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()


def configured_webhook_url() -> str:
    """Read the Discord webhook from a secret, without ever showing it in the UI."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if webhook_url:
        return webhook_url

    try:
        return str(st.secrets.get("discord_webhook_url", "")).strip()
    except Exception:
        return ""


def send_application_to_discord(
    webhook_url: str,
    discord_username: str,
    birth_date: date,
    role: str,
    answers: list[tuple[str, str]],
) -> tuple[bool, str]:
    """Send an application to a configured Discord channel through a webhook."""
    trusted_webhook_prefixes = (
        "https://discord.com/api/webhooks/",
        "https://discordapp.com/api/webhooks/",
    )
    if not webhook_url.startswith(trusted_webhook_prefixes):
        return False, "The staff webhook is not configured as a valid Discord webhook."

    fields = [
        {"name": "Discord username", "value": discord_username, "inline": True},
        {"name": "Date of birth", "value": birth_date.isoformat(), "inline": True},
        {"name": "Role requested", "value": role, "inline": True},
    ]
    for question_number, (question, answer) in enumerate(answers, start=1):
        fields.append(
            {
                "name": f"Question {question_number}",
                "value": f"**{question}**\n{answer}",
                "inline": False,
            }
        )

    payload = {
        "username": "True Surviving SMP • Staff Apps",
        "allowed_mentions": {"parse": []},
        "embeds": [
            {
                "title": "New Staff Application",
                "description": "Review this application with the staff team and record an approve or decline decision.",
                "color": 2858323,
                "fields": fields,
                "footer": {"text": "True Surviving SMP • Staff application review"},
            }
        ],
    }
    request = Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "TrueSurvivingSMP/1.0"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            if response.status not in (200, 204):
                return False, "Discord did not accept the application. Please try again later."
    except HTTPError:
        return False, "Discord did not accept the application. Please try again later."
    except URLError:
        return False, "The staff delivery channel could not be reached. Please try again later."

    return True, ""


def show_staff_application() -> None:
    """Show role-specific staff questions and deliver completed applications to Discord."""
    st.markdown(
        """
        <section class="staff-hero">
          <div class="staff-kicker">TRUE SURVIVING SMP &bull; STAFF RECRUITMENT</div>
          <div class="staff-title">STAFF APPLICATION</div>
          <p class="staff-copy">Choose the role that fits your experience. Every application is reviewed by the staff team with care.</p>
          <div class="staff-status"><span>FAIR REVIEW</span><span>ROLE-BASED QUESTIONS</span><span>STAFF ONLY</span></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='staff-section-label'>01 &bull; YOUR DETAILS</div>", unsafe_allow_html=True)
    discord_username = st.text_input(
        "Discord username",
        placeholder="Example: PlayerName",
        max_chars=64,
        key="staff-discord-username",
    )
    birth_date = st.date_input(
        "Date of birth",
        min_value=date(1930, 1, 1),
        max_value=date.today(),
        value=None,
        format="DD/MM/YYYY",
        key="staff-birth-date",
    )

    st.markdown("<div class='staff-section-label'>02 &bull; STAFF ROLE</div>", unsafe_allow_html=True)
    role = st.selectbox(
        "Choose the staff role you are applying for",
        options=tuple(ROLE_QUESTIONS),
        index=None,
        placeholder="Select a role",
        key="staff-role",
    )

    answers: list[tuple[str, str]] = []
    if role:
        role_info = ROLE_QUESTIONS[role]
        st.markdown(
            f"<div class='staff-role-note'><strong>{role_info['level']}</strong><br>{role_info['description']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='staff-section-label'>03 &bull; ROLE QUESTIONS</div>", unsafe_allow_html=True)
        st.markdown("<div class='staff-question-card'>", unsafe_allow_html=True)
        for number, (question, choices) in enumerate(role_info["questions"], start=1):
            st.markdown(
                f"<div class='staff-question-heading'>QUESTION {number:02d}</div>",
                unsafe_allow_html=True,
            )
            answer = st.radio(
                question,
                options=choices,
                index=None,
                key=f"staff-{role}-question-{number}",
            )
            if answer:
                answers.append((question, answer))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='staff-section-label'>04 &bull; SUBMIT FOR REVIEW</div>", unsafe_allow_html=True)
    consent = st.checkbox(
        "I understand that my Discord username, date of birth, role, and answers will be sent privately to the staff team for application review.",
        key="staff-consent",
    )
    st.markdown(
        "<div class='staff-privacy'>Applications are sent only to the configured private staff Discord channel. Do not enter passwords, account codes, or other sensitive information.</div>",
        unsafe_allow_html=True,
    )

    if st.button("Submit staff application", key="submit-staff-application", use_container_width=True):
        errors = []
        if not discord_username.strip():
            errors.append("Enter your Discord username.")
        if birth_date is None:
            errors.append("Select your date of birth.")
        if not role:
            errors.append("Choose a staff role.")
        elif len(answers) != len(ROLE_QUESTIONS[role]["questions"]):
            errors.append("Answer every role question before submitting.")
        if not consent:
            errors.append("Confirm that the staff team may review this application.")

        if errors:
            st.error(" ".join(errors))
        else:
            webhook_url = configured_webhook_url()
            if not webhook_url:
                st.error("Applications are not open yet because the private staff webhook has not been configured.")
            else:
                with st.spinner("Sending your application to the staff team..."):
                    sent, message = send_application_to_discord(
                        webhook_url,
                        discord_username.strip(),
                        birth_date,
                        role,
                        answers,
                    )
                if sent:
                    st.success("Application sent! The staff team can now review it in their private Discord channel.")
                else:
                    st.error(message)

    if st.button("Back to main menu", key="staff-back-to-menu", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()


def show_violation_punishments() -> None:
    """Display the server's five-level violation punishment ladder."""
    st.markdown(
        """
        <section class="punishment-hero">
          <div class="punishment-kicker">TRUE SURVIVING SMP &bull; FAIR PLAY SYSTEM</div>
          <div class="punishment-title">VIOLATION PUNISHMENTS</div>
          <p class="punishment-copy">Punishments increase when violations continue or become more serious. Keep the server fair, clean, and fun for everyone.</p>
        </section>

        <section class="punishment-ladder">
          <article class="punishment-card level-1">
            <div class="punishment-stage">01</div>
            <div><div class="punishment-label">First or small violation</div><div class="punishment-action">Warning</div></div>
            <div class="punishment-badge">LEVEL 1</div>
          </article>
          <article class="punishment-card level-2">
            <div class="punishment-stage">02</div>
            <div><div class="punishment-label">Second or medium violation</div><div class="punishment-action">Last warning</div></div>
            <div class="punishment-badge">LEVEL 2</div>
          </article>
          <article class="punishment-card level-3">
            <div class="punishment-stage">03</div>
            <div><div class="punishment-label">Third or high violation</div><div class="punishment-action">1 day mute</div></div>
            <div class="punishment-badge">LEVEL 3</div>
          </article>
          <article class="punishment-card level-4">
            <div class="punishment-stage">04</div>
            <div><div class="punishment-label">Fourth or intermediate violation</div><div class="punishment-action">Kick</div></div>
            <div class="punishment-badge">LEVEL 4</div>
          </article>
          <article class="punishment-card level-5">
            <div class="punishment-stage">05</div>
            <div><div class="punishment-label">Fifth or final violation level</div><div class="punishment-action">Ban for 7 days or permanent ban</div></div>
            <div class="punishment-badge">FINAL LEVEL</div>
          </article>
        </section>

        <div class="punishment-footer">Staff will use this escalation system to keep decisions clear and consistent across the server.</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Back to main menu", key="punishment-back-to-menu", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()


page_style()
if "view" not in st.session_state:
    st.session_state.view = "home"

if st.session_state.view == "rules":
    show_rules()
elif st.session_state.view == "terms":
    show_terms()
elif st.session_state.view == "staff":
    show_staff_application()
elif st.session_state.view == "punishments":
    show_violation_punishments()
else:
    show_logo()
    st.markdown(
        "<div class='home-console'>"
        "<span class='console-chip code'>&lt;/&gt; SERVER_CORE</span>"
        "<span class='console-chip online'><span class='live-dot'></span>SMP ONLINE</span>"
        "<span class='mc-blocks' aria-label='Minecraft blocks'><span class='mc-block grass'></span><span class='mc-block stone'></span><span class='mc-block ore'></span></span>"
        "</div>"
        "<div class='brand-lockup'>"
        "<div class='brand-name'>True surviving smp</div>"
        "<div class='brand-tagline'>True vanilla+ experience</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    options = ("Terms of service", "Rules", "Staff applications", "Violation punishment")
    for option in options:
        if st.button(option, key=option.lower().replace(" ", "-"), use_container_width=True):
            if option == "Terms of service":
                st.session_state.view = "terms"
                st.rerun()
            if option == "Rules":
                st.session_state.view = "rules"
                st.rerun()
            if option == "Staff applications":
                st.session_state.view = "staff"
                st.rerun()
            if option == "Violation punishment":
                st.session_state.view = "punishments"
                st.rerun()
            st.toast(f"{option} selected", icon="✅")
