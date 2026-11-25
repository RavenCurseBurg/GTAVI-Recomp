# Discord server

The project's Discord server, [discord.gg/RTwXeccCqD](https://discord.gg/RTwXeccCqD),
is where development updates are posted and discussed. This page is the source
of truth for its layout and text: change it here first, then copy the change to
Discord, so the server can be rebuilt from this file.

[`scripts/discord_setup.py`](../../scripts/discord_setup.py) builds this layout
through the Discord API with a bot token and posts the welcome, rules and FAQ
messages from this file. See [Building the server](#building-the-server).

- [Channel layout](#channel-layout)
- [Roles](#roles)
- [Automatic updates](#automatic-updates)
- [Rules](#rules)
- [Welcome message](#welcome-message)
- [FAQ](#faq)

## Channel layout

Read-only channels let everyone read but only maintainers and the update
webhooks post.

| Category | Channel | Purpose | Who can post |
| --- | --- | --- | --- |
| **Start here** | `#welcome` | Welcome message and links | Maintainers |
| | `#rules` | The rules below | Maintainers |
| | `#faq` | The FAQ below | Maintainers |
| | `#announcements` | Releases and major news | Maintainers, release webhook |
| **Progress** | `#progress` | Commits to `main` with the roadmap and AnyPS5 numbers | Progress webhook |
| **Community** | `#general` | General discussion about the project | Everyone |
| | `#ideas` | Suggestions for the project and the server | Everyone |
| | `#off-topic` | Anything else that follows the rules | Everyone |
| **Development** | `#research` | PS5 platform research from public sources and AnyPS5 | Everyone |
| | `#anyps5-upstream` | Library and shader work going upstream to AnyPS5 | Everyone |
| | `#dev-chat` | This repository: docs, tooling, progress, CI | Everyone |
| | `#build-help` | Building this repository and AnyPS5 | Everyone |
| **Voice** | `General` | Voice chat | Everyone |
| **Staff** | `#member-log` | Joins and leaves, posted by Cal. Hidden from members | Cal (Moderators read) |

No channel is for sharing or requesting game files, and none should be added.

## Roles

| Role | Who | Permissions beyond `@everyone` |
| --- | --- | --- |
| `Maintainer` | Project maintainers | Administrator |
| `Moderator` | Trusted members who enforce the rules | Manage messages, timeout members, view audit log |
| `Contributor` | Anyone with a merged pull request here or upstream in AnyPS5 | None; recognition only |
| `Updates` | Members who opt in to pings | Pinged on `#announcements` posts |

The bot, **Cal Hampton**, has its own role with only **Manage Roles**, placed
above `Updates` so `/updates` can give that role out. Its commands and VPS setup
are in [bot/README.md](../../bot/README.md).

`@everyone` can read every channel, post in the Community and Development
channels, and join voice. Nobody but maintainers and moderators can mention
`@everyone` or `@here`.

## Automatic updates

[`.github/workflows/discord.yml`](../../.github/workflows/discord.yml) posts
through Discord webhooks, using [`scripts/discord_notify.py`](../../scripts/discord_notify.py):

- **Pushes to `main`** go to `#progress`: the new commits, with the roadmap and
  AnyPS5 numbers from `scripts/update_progress.py`.
- **Published GitHub releases** go to `#announcements`.

Each webhook URL is a secret, so the maintainer sets it up; it is never committed:

1. In Discord, open the channel's settings, then **Integrations → Webhooks →
   New Webhook**, and copy its URL.
2. On GitHub, open **Settings → Secrets and variables → Actions → New
   repository secret**:
   - `DISCORD_WEBHOOK_PROGRESS` for `#progress`
   - `DISCORD_WEBHOOK_ANNOUNCEMENTS` for `#announcements`

A workflow run with no secret set skips posting instead of failing. Posts never
ping anyone, whatever a commit message contains.

## Building the server

Run `python scripts/discord_setup.py --offline` to preview every welcome, rules
and FAQ message from this file. It prints the embed sizes and complete message
payloads before you need a bot token.

1. In the [Discord Developer Portal](https://discord.com/developers/applications),
   create an application, open **Bot**, and reset the token to copy it. Treat it
   like a password: never commit it or paste it anywhere public.
2. Under **OAuth2 → URL Generator**, tick the `bot` scope and the
   `Administrator` permission, open the generated URL and add the bot to the
   server.
3. In a terminal, set the token for that terminal only and run a plan, which
   reads the server and changes nothing:

   ```powershell
   $env:DISCORD_BOT_TOKEN = Read-Host -MaskInput "Bot token"
   python scripts/discord_setup.py
   ```

4. If the plan looks right, apply it. Add `--webhooks` to also create the
   `#progress` and `#announcements` webhooks; their URLs are printed once for the
   GitHub secrets:

   ```powershell
   python scripts/discord_setup.py --apply --webhooks
   ```

5. Take away the bot's Administrator permission when done. The same bot runs
   the server's slash commands; see [bot/README.md](../../bot/README.md) for
   the permissions it keeps.

The script matches roles and channels by name, reuses ones that exist, never
deletes or renames anything, and posts a message only to a channel that has none
from the bot yet, so it is safe to run again after editing this file.

## Rules

> **1. No game files, keys or piracy.** Do not share, request or link GTA VI
> files, PS5 system files or firmware, decryption keys, dumps, decrypted
> executables, converted executables, leaked material or pirated copies. Do not
> ask how to obtain them or explain how to. This includes DMs started from this
> server. Breaking this rule is a ban without warning.
>
> **2. No converted builds.** A GTA VI executable converted with AnyPS5 is
> derived from the game and is never shared, here or anywhere linked from here.
>
> **3. Be respectful.** No harassment, hate speech, personal attacks or doxxing.
> Disagree with ideas, not people.
>
> **4. Stay on topic.** Use the channel that fits. Keep general GTA VI talk to
> `#off-topic`.
>
> **5. No release-date pressure.** There is no ETA. Repeated "when will it work?"
> messages will be removed; the progress page and `#progress` show where things
> stand.
>
> **6. No spam or self-promotion.** No ads, unsolicited DMs, invite links or
> referral links.
>
> **7. Keep it safe for work.** No NSFW content, including in names and avatars.
>
> **8. Follow Discord's rules.** The [Terms of Service](https://discord.com/terms)
> and [Community Guidelines](https://discord.com/guidelines) apply.
>
> This is an independent project, not affiliated with Rockstar Games, Take-Two
> Interactive or Sony Interactive Entertainment. Moderators may act on anything
> that puts the project or its members at legal risk, even if no rule names it.

## Welcome message

> **Welcome to the GTA VI Translation Layer community!**
>
> This project aims to run the PS5 build of GTA VI natively on PC, built on
> [AnyPS5](https://github.com/boykopovar/AnyPS5). It is early: the game does not
> run, and there is no release date.
>
> **Start here**
> - Read `#rules`. Rule 1 matters most: no game files, keys or piracy, ever.
> - Check `#faq` before asking.
> - Follow development in `#progress`, or on the
>   [progress page](https://jamescicada.github.io/GTAVI-Recomp/).
>
> **Want to help?** Read the [repository](https://github.com/JamesCicada/GTAVI-Recomp)
> and [CONTRIBUTE.md](https://github.com/JamesCicada/GTAVI-Recomp/blob/main/CONTRIBUTE.md),
> then say hi in `#dev-chat`. Research, documentation and library work in AnyPS5
> all count.

## FAQ

> **Does GTA VI run on PC with this?**
> No. Nothing has been tested with the game yet.
>
> **When will it work?**
> There is no ETA. The [progress page](https://jamescicada.github.io/GTAVI-Recomp/)
> shows what is done, what is open, and what is blocked.
>
> **How is it supposed to work?**
> [AnyPS5](https://github.com/boykopovar/AnyPS5) converts a PS5 executable into a
> native Windows or Linux program and supplies its own versions of the PS5 system
> libraries. The game's code runs directly on your PC's processor; nothing is
> emulated. This project builds on AnyPS5 and adds what GTA VI needs.
>
> **Why is so much "blocked on game files"?**
> Studying the game needs a decrypted executable, and the project will not
> obtain or use one unlawfully. Until GTA VI's files can be researched lawfully,
> work focuses on what does not need them.
>
> **Will you share the game, a dump or a converted build?**
> No, never. Asking is against rule 1.
>
> **Is this an emulator?**
> No. Emulators imitate the console's hardware. This approach runs the game's
> own code natively and only replaces the system libraries it calls.
>
> **What about the Xbox version?**
> Technically closer to PC, but much harder to obtain lawfully for study, and
> nothing like AnyPS5 exists for it. The project targets the PS5 build.
>
> **What about GTA Online?**
> Out of scope. GTA VI has no online mode released.
>
> **How can I help?**
> Read the repository's README and CONTRIBUTE.md. Useful work right now:
> library implementations upstream in AnyPS5, research from public sources,
> documentation, and tooling. Ask in `#dev-chat`.
>
> **Is this legal?**
> The project contains only its own code and documentation, and follows a strict
> no-game-files policy. Obtaining or decrypting game files yourself can be
> illegal where you live; that is your responsibility. This is not legal advice.
>
> **Is this affiliated with Rockstar, Take-Two or Sony?**
> No.
