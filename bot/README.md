# Cal Hampton

The project's Discord bot. It answers three slash commands in the
[project server](../docs/community/discord.md):

| Command | What it does | Who sees the reply |
| --- | --- | --- |
| `/progress` | Roadmap, shader and library progress, with bars | Everyone in the channel |
| `/faq [topic]` | The answer to a FAQ question; without a topic, the list of questions | Answer: everyone; list: only you |
| `/updates` | Gives you the `Updates` role, or removes it, to turn announcement pings on or off | Only you |

`/progress` reads the published [progress page](https://jamescicada.github.io/GTAVI-Recomp/)'s
`progress.json`, and `/faq` reads the FAQ in
[docs/community/discord.md](../docs/community/discord.md) on `main`. Both are
cached for five minutes, so the bot follows `main` without being redeployed.

## Member events

Two optional features, each switched on by an environment variable in
`/etc/cal-hampton.env`:

| Variable | What Cal does |
| --- | --- |
| `CAL_WELCOME_CHANNEL=general` | Greets each new member there, pinging them, with links to `#rules` and `#faq`. Bots are not greeted. |
| `CAL_LOG_CHANNEL=member-log` | Logs every join (account age, ID, a warning for accounts under 7 days old) and leave (when they joined, their roles) as embeds that ping nobody. |

Values are a channel name or ID. Either one needs the privileged **Server
Members Intent** (Developer Portal → **Bot** → **Privileged Gateway Intents**);
switch it on first, or Discord refuses Cal's connection. With neither set, Cal
does not ask for the intent.

The hidden `#member-log` channel is created by
[`scripts/discord_setup.py`](../scripts/discord_setup.py): `@everyone` cannot
see it, Moderators can read it, and Cal's role can post in it.

## Discord setup

1. **Permissions.** Cal needs only **Manage Roles**. In Discord, open
   **Server Settings → Roles → Cal Hampton**, turn **Administrator** off and
   **Manage Roles** on. (Run the setup script, which needs Administrator,
   before taking it away.)
2. **Role order.** In the same list, drag the **Cal Hampton** role above
   **Updates**. A bot can only give out roles below its own.
3. **Intents.** Only the member events above need a privileged intent
   (**Server Members**). Leave the others off.

## Running on a VPS (systemd)

These steps assume a Linux VPS with Python 3.10 or newer and systemd.

```bash
# A user with no login shell or home directory, just for the bot.
sudo useradd --system --no-create-home --shell /usr/sbin/nologin calbot

# Code and a virtual environment in /opt/cal-hampton.
sudo git clone https://github.com/JamesCicada/GTAVI-Recomp.git /opt/cal-hampton
sudo python3 -m venv /opt/cal-hampton/venv
sudo /opt/cal-hampton/venv/bin/pip install -r /opt/cal-hampton/bot/requirements.txt

# The token, readable only by root (systemd reads it before dropping to calbot).
sudo install -m 600 /dev/null /etc/cal-hampton.env
sudoedit /etc/cal-hampton.env
#   DISCORD_BOT_TOKEN=paste-the-token-here

# Install and start the service.
sudo cp /opt/cal-hampton/bot/cal-hampton.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cal-hampton
```

Check it:

```bash
systemctl status cal-hampton
journalctl -u cal-hampton -f     # "Registered 3 commands" and "Logged in as Cal Hampton"
```

The clone in `/opt/cal-hampton` is a full checkout of the repository, but the bot
only runs `bot/`. It does not need the AnyPS5 submodule.

## Updating

```bash
sudo git -C /opt/cal-hampton pull
sudo /opt/cal-hampton/venv/bin/pip install -r /opt/cal-hampton/bot/requirements.txt
sudo systemctl restart cal-hampton
```

Changes to the FAQ or the progress numbers do not need a restart.

## Security

- The token lives only in `/etc/cal-hampton.env` on the VPS. Never commit it,
  paste it in chat, or put it in the service file.
- If it leaks, reset it in the Developer Portal (**Bot → Reset Token**), update
  `/etc/cal-hampton.env`, and restart the service.
- The service runs as the unprivileged `calbot` user with a read-only view of
  the system (`ProtectSystem=strict`).

## Running locally

```powershell
python -m venv .venv-bot
.\.venv-bot\Scripts\pip install -r bot\requirements.txt
$env:DISCORD_BOT_TOKEN = Read-Host -MaskInput "Bot token"
.\.venv-bot\Scripts\python bot\cal_hampton.py
```

Only run one copy at a time: two copies would both answer each command.

With the bot dependencies installed, run `python -m unittest discover -s bot`
from the repository root to test FAQ responses offline.
