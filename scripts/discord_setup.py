#!/usr/bin/env python3
"""Build the project's Discord server layout through the Discord REST API.

The layout below mirrors docs/community/discord.md, and the welcome, rules and
FAQ messages are read from that file, so it stays the source of truth.

Usage:
    # Preview the welcome, rules and FAQ messages locally.
    python scripts/discord_setup.py --offline

    # 1. Plan only: reads the server and prints what would change.
    python scripts/discord_setup.py
    # 2. Make the changes.
    python scripts/discord_setup.py --apply
    # Optional: create the #progress and #announcements webhooks and print
    # their URLs once, for the GitHub secrets.
    python scripts/discord_setup.py --apply --webhooks

The bot token is read from the DISCORD_BOT_TOKEN environment variable and is
never printed. The bot needs the Administrator permission while this runs
(it creates an Administrator role and channel permission overwrites); remove
it from the server afterwards if you like.

The script is idempotent: roles and channels are matched by name, existing ones
are reused (and moved into the right category), and the welcome, rules and FAQ
messages are only posted to a channel that has no message from the bot yet.
Nothing existing is deleted or renamed. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "community" / "discord.md"
API = "https://discord.com/api/v10"
USER_AGENT = "DiscordBot (https://github.com/JamesCicada/GTAVI-Recomp, 1.0)"
DEFAULT_GUILD = "1573077095201120322"

# Channel types and permission bits from the Discord API documentation.
TEXT, VOICE, CATEGORY = 0, 2, 4
ADMINISTRATOR = 1 << 3
ADD_REACTIONS = 1 << 6
VIEW_AUDIT_LOG = 1 << 7
VIEW_CHANNEL = 1 << 10
SEND_MESSAGES = 1 << 11
MANAGE_MESSAGES = 1 << 13
MENTION_EVERYONE = 1 << 17
CREATE_PUBLIC_THREADS = 1 << 35
CREATE_PRIVATE_THREADS = 1 << 36
SEND_MESSAGES_IN_THREADS = 1 << 38
MODERATE_MEMBERS = 1 << 40

EMBED_LINKS = 1 << 14
READ_MESSAGE_HISTORY = 1 << 16

READ_ONLY_DENY = SEND_MESSAGES | SEND_MESSAGES_IN_THREADS | CREATE_PUBLIC_THREADS | CREATE_PRIVATE_THREADS

ROLES = [
    # name, permissions, colour, hoist (shown separately), mentionable
    ("Maintainer", ADMINISTRATOR, 0xF85149, True, False),
    ("Moderator", MANAGE_MESSAGES | MODERATE_MEMBERS | VIEW_AUDIT_LOG | MENTION_EVERYONE, 0xD29922, True, False),
    ("Contributor", 0, 0x2EA043, True, False),
    ("Updates", 0, 0, False, True),
]

# category -> [(channel name, type, topic, access)]
# access: "open" (everyone posts), "read-only" (everyone reads, only admins and
# webhooks post), "staff" (hidden; Moderators read, the bot posts).
LAYOUT = [
    ("Start here", [
        ("welcome", TEXT, "Welcome to the GTA VI Translation Layer community. Start here.", "read-only"),
        ("rules", TEXT, "Server rules. Rule 1: no game files, keys or piracy, ever.", "read-only"),
        ("faq", TEXT, "Frequently asked questions. Read before asking.", "read-only"),
        ("announcements", TEXT, "Releases and major news.", "read-only"),
    ]),
    ("Progress", [
        ("progress", TEXT, "Commits to main with roadmap and AnyPS5 numbers. https://jamescicada.github.io/GTAVI-Recomp/", "read-only"),
    ]),
    ("Community", [
        ("general", TEXT, "General discussion about the project.", "open"),
        ("ideas", TEXT, "Suggestions for the project and the server.", "open"),
        ("off-topic", TEXT, "Anything else that follows the rules.", "open"),
    ]),
    ("Development", [
        ("research", TEXT, "PS5 platform research from public sources and AnyPS5. No game files.", "open"),
        ("anyps5-upstream", TEXT, "Library and shader work going upstream to AnyPS5.", "open"),
        ("dev-chat", TEXT, "This repository: docs, tooling, progress, CI.", "open"),
        ("build-help", TEXT, "Building this repository and AnyPS5.", "open"),
    ]),
    ("Voice", [
        ("General", VOICE, None, "open"),
    ]),
    ("Staff", [
        ("member-log", TEXT, "Joins and leaves, posted by Cal. Staff only.", "staff"),
    ]),
]

# channel -> heading in docs/community/discord.md whose blockquote is posted there.
MESSAGES = {"welcome": "Welcome message", "rules": "Rules", "faq": "FAQ"}
WEBHOOK_CHANNELS = {"progress": "DISCORD_WEBHOOK_PROGRESS", "announcements": "DISCORD_WEBHOOK_ANNOUNCEMENTS"}
EMBED_COLOUR = 0x2F81F7
EMBED_LIMIT = 4096


# --------------------------------------------------------------------------
# API


class Discord:
    def __init__(self, token: str):
        self.token = token

    def call(self, method: str, path: str, body: dict | None = None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        for _ in range(5):
            request = urllib.request.Request(
                API + path,
                data=data,
                method=method,
                headers={
                    "Authorization": f"Bot {self.token}",
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    raw = response.read()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", "replace")
                if error.code == 429:
                    wait = float(json.loads(detail).get("retry_after", 1.0))
                    time.sleep(wait + 0.2)
                    continue
                raise SystemExit(f"discord_setup: {method} {path} failed with HTTP {error.code}: {detail[:500]}")
            except urllib.error.URLError as error:
                raise SystemExit(f"discord_setup: could not reach Discord: {error.reason}")
        raise SystemExit(f"discord_setup: {method} {path} kept hitting the rate limit")


# --------------------------------------------------------------------------
# Docs


def blockquote(markdown: str, heading: str) -> str:
    """The blockquote under '## heading', without the '> ' prefixes."""
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", markdown, re.M | re.S)
    if not match:
        raise SystemExit(f"discord_setup: no '## {heading}' section in {DOC.relative_to(ROOT)}")
    lines = [line[2:] if line.startswith("> ") else line[1:] if line.startswith(">") else None
             for line in match.group(1).splitlines()]
    text = "\n".join(line for line in lines if line is not None).strip()
    if not text:
        raise SystemExit(f"discord_setup: '## {heading}' has no blockquote")
    return unwrap(text)


def unwrap(text: str) -> str:
    """Join hard-wrapped lines: Discord shows every newline, Markdown does not.

    A line break is kept before list items, before a line starting in bold, and
    after a line that is only a bold heading (such as each FAQ question).
    """
    paragraphs = []
    for paragraph in text.split("\n\n"):
        out = ""
        for line in paragraph.splitlines():
            line = line.strip()
            if not out:
                out = line
            elif line.startswith(("- ", "* ", "**")) or out.endswith("**"):
                out += "\n" + line
            else:
                out += " " + line
        paragraphs.append(out)
    return "\n\n".join(paragraphs)


def embeds_for(text: str, title: str) -> list[dict]:
    """Prefer paragraph breaks and wrap paragraphs that exceed the embed limit."""
    chunks, current = [], ""
    for paragraph in text.split("\n\n"):
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) > EMBED_LIMIT and current:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate
        if len(current) > EMBED_LIMIT:
            parts = textwrap.wrap(current, width=EMBED_LIMIT, expand_tabs=False,
                                  replace_whitespace=False, drop_whitespace=False)
            chunks.extend(parts[:-1])
            current = parts[-1]
    chunks.append(current)
    return [
        {"title": title if i == 0 else None, "description": chunk, "color": EMBED_COLOUR}
        for i, chunk in enumerate(chunks)
    ]


def message_payload(embed: dict) -> dict:
    return {"embeds": [{k: v for k, v in embed.items() if v is not None}],
            "allowed_mentions": {"parse": []}}


# --------------------------------------------------------------------------
# Plan and apply


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--guild", default=DEFAULT_GUILD, help="server ID")
    parser.add_argument("--apply", action="store_true", help="make the changes (default: plan only)")
    parser.add_argument("--webhooks", action="store_true",
                        help="create #progress and #announcements webhooks and print their URLs once")
    parser.add_argument("--offline", action="store_true",
                        help="print the messages that would be posted, without contacting Discord")
    args = parser.parse_args()

    markdown = DOC.read_text(encoding="utf-8")
    messages = {channel: embeds_for(blockquote(markdown, heading), heading)
                for channel, heading in MESSAGES.items()}

    if args.offline:
        preview = {}
        for channel, embeds in messages.items():
            print(f"#{channel}: {len(embeds)} embed(s)")
            for embed in embeds:
                print(f"  {len(embed['description'])} characters")
            preview[channel] = [message_payload(embed) for embed in embeds]
        try:
            print(json.dumps(preview, indent=2, ensure_ascii=False))
        except UnicodeEncodeError:
            # Preserve the message text as JSON escapes on legacy output encodings.
            print(json.dumps(preview, indent=2))
        return 0

    token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("discord_setup: set DISCORD_BOT_TOKEN in this terminal first (see the script's docstring)")
    api = Discord(token)
    apply = args.apply
    mode = "APPLY" if apply else "PLAN (nothing is changed; rerun with --apply)"
    print(f"Mode: {mode}\n")

    me = api.call("GET", "/users/@me")
    guild = api.call("GET", f"/guilds/{args.guild}")
    print(f"Bot: {me['username']}  Server: {guild['name']}\n")
    everyone_id = args.guild  # @everyone's role ID equals the server ID.

    # Roles
    roles = {r["name"]: r for r in api.call("GET", f"/guilds/{args.guild}/roles")}
    for name, permissions, colour, hoist, mentionable in ROLES:
        if name in roles:
            print(f"  role {name}: exists, left as is")
            continue
        print(f"+ role {name}")
        if apply:
            roles[name] = api.call("POST", f"/guilds/{args.guild}/roles", {
                "name": name, "permissions": str(permissions), "color": colour,
                "hoist": hoist, "mentionable": mentionable,
            })

    everyone = roles.get("@everyone") or next(r for r in roles.values() if r["id"] == everyone_id)
    everyone_perms = int(everyone["permissions"])
    if everyone_perms & MENTION_EVERYONE:
        print("~ @everyone: remove 'Mention @everyone, @here and all roles'")
        if apply:
            api.call("PATCH", f"/guilds/{args.guild}/roles/{everyone_id}",
                     {"permissions": str(everyone_perms & ~MENTION_EVERYONE)})
    else:
        print("  @everyone: already cannot mention @everyone")

    # The bot's own managed role, so staff channels can let it post.
    bot_role = next((r for r in roles.values() if (r.get("tags") or {}).get("bot_id") == me["id"]), None)

    def channel_overwrites(access: str) -> list[dict]:
        if access == "read-only":
            return [{"id": everyone_id, "type": 0, "allow": "0", "deny": str(READ_ONLY_DENY)}]
        if access == "staff":
            out = [{"id": everyone_id, "type": 0, "allow": "0", "deny": str(VIEW_CHANNEL)}]
            moderator = roles.get("Moderator")
            if moderator:
                out.append({"id": moderator["id"], "type": 0,
                            "allow": str(VIEW_CHANNEL | READ_MESSAGE_HISTORY), "deny": "0"})
            if bot_role:
                out.append({"id": bot_role["id"], "type": 0,
                            "allow": str(VIEW_CHANNEL | SEND_MESSAGES | EMBED_LINKS | READ_MESSAGE_HISTORY),
                            "deny": "0"})
            else:
                out.append({"id": me["id"], "type": 1,
                            "allow": str(VIEW_CHANNEL | SEND_MESSAGES | EMBED_LINKS | READ_MESSAGE_HISTORY),
                            "deny": "0"})
            return out
        return []

    # Channels
    channels = api.call("GET", f"/guilds/{args.guild}/channels")

    def find(name: str, kind: int):
        return next((c for c in channels if c["name"].lower() == name.lower() and c["type"] == kind), None)

    created: dict[str, dict] = {}
    for position, (category_name, children) in enumerate(LAYOUT):
        category = find(category_name, CATEGORY)
        if category:
            print(f"  category {category_name}: exists")
        else:
            print(f"+ category {category_name}")
            if apply:
                category = api.call("POST", f"/guilds/{args.guild}/channels",
                                    {"name": category_name, "type": CATEGORY, "position": position})
                channels.append(category)
        for name, kind, topic, access in children:
            overwrites = channel_overwrites(access)
            existing = find(name, kind)
            label = f"#{name}" if kind == TEXT else name
            if existing:
                if category and existing.get("parent_id") != category["id"]:
                    print(f"~ {label}: move into {category_name}")
                    if apply:
                        api.call("PATCH", f"/channels/{existing['id']}", {"parent_id": category["id"]})
                elif not category:
                    print(f"~ {label}: move into {category_name}")
                else:
                    print(f"  {label}: exists in {category_name}")
                created[name] = existing
                continue
            print(f"+ {label} in {category_name}" + (f" ({access})" if access != "open" else ""))
            if apply:
                body = {"name": name, "type": kind, "parent_id": category["id"],
                        "permission_overwrites": overwrites}
                if topic:
                    body["topic"] = topic
                channel = api.call("POST", f"/guilds/{args.guild}/channels", body)
                channels.append(channel)
                created[name] = channel

    # Messages
    for channel_name, embeds in messages.items():
        channel = created.get(channel_name)
        if channel is None:
            print(f"+ post {MESSAGES[channel_name]} in #{channel_name} ({len(embeds)} message(s))")
            continue
        recent = api.call("GET", f"/channels/{channel['id']}/messages?limit=50")
        if any(m["author"]["id"] == me["id"] for m in recent):
            print(f"  #{channel_name}: already has a message from the bot, not posting again")
            continue
        print(f"+ post {MESSAGES[channel_name]} in #{channel_name} ({len(embeds)} message(s))")
        if apply:
            for embed in embeds:
                api.call("POST", f"/channels/{channel['id']}/messages", message_payload(embed))

    # Webhooks
    if args.webhooks:
        for channel_name, secret in WEBHOOK_CHANNELS.items():
            channel = created.get(channel_name)
            print(f"+ webhook for #{channel_name} -> GitHub secret {secret}")
            if apply and channel:
                hook = api.call("POST", f"/channels/{channel['id']}/webhooks", {"name": "GTAVI-Recomp"})
                print(f"    {secret} = https://discord.com/api/webhooks/{hook['id']}/{hook['token']}")
        if apply:
            print("\nThe webhook URLs above are secrets: add them to GitHub, then clear this terminal.")

    print("\nDone." if apply else "\nPlan only. Rerun with --apply to make these changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
