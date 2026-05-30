---
name: telegram-gateway-operations
description: Diagnose and safely operate Telegram Comms Gate behavior for Hermes bots, groups, forum topics, pinned messages, topic renames, admin permissions, and Bot API verification.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [telegram, gateway, bot-api, forum-topics, pinned-messages]
    related_skills: [hermes-agent, terminal-command-guidance]
---

# Telegram Gateway Operations

Use this Skill Rune when a user reports strange Telegram behavior around Hermes: pinned messages reappearing, topic renames, forum topics, wrong thread delivery, bot admin permissions, group/topic routing, or suspected Telegram Comms Gate corruption.

For the concrete forum-topic pattern where a pinned banner says a user renamed a topic and keeps returning after deletion, load `references/forum-pinned-service-message.md`.

## Purpose

Separate Telegram platform behavior from Hermes bugs or compromise. Inspect first, report plainly, and only mutate Telegram state after explicit approval.

## Required Access Keys

- Telegram bot token available to the runtime, usually `TELEGRAM_BOT_TOKEN` in `/home/ubuntu/.hermes/.env` or systemd environment.
- Target `chat_id`; for forum topics also capture `message_thread_id` if known.

Never print the bot token. Load it inside a script and only print sanitized metadata.

## Phase 1 — Read-only inspection

First determine whether the issue is Telegram state, Hermes behavior, or an external/admin action.

Read-only Bot API checks:

```bash
python3 - <<'PY'
import os, json, urllib.request, urllib.parse, pathlib

# Load token without printing it.
for env_path in [pathlib.Path('/home/ubuntu/.hermes/.env')]:
    if env_path.exists():
        for line in env_path.read_text(errors='ignore').splitlines():
            if line.strip().startswith('TELEGRAM_BOT_TOKEN='):
                os.environ['TELEGRAM_BOT_TOKEN'] = line.split('=', 1)[1].strip().strip('"\'')
                break

token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '<chat_id_here>')
if not token:
    raise SystemExit('TELEGRAM_BOT_TOKEN missing')

base = f'https://api.telegram.org/bot{token}/'
def call(method, params):
    url = base + method + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)

for method in ['getChat', 'getChatAdministrators']:
    data = call(method, {'chat_id': chat_id})
    print('---', method, '---')
    if method == 'getChat':
        res = data.get('result', {})
        pinned = res.get('pinned_message')
        if isinstance(pinned, dict):
            pinned = {k: pinned.get(k) for k in [
                'message_id', 'date', 'message_thread_id', 'from',
                'text', 'forum_topic_created', 'forum_topic_edited',
                'pinned_message'
            ]}
        print({k: res.get(k) for k in ['id', 'title', 'type', 'is_forum', 'permissions']})
        print('pinned_message:', pinned)
    else:
        for admin in data.get('result', []):
            user = admin.get('user', {})
            print({
                'status': admin.get('status'),
                'id': user.get('id'),
                'username': user.get('username'),
                'is_bot': user.get('is_bot'),
                'can_pin_messages': admin.get('can_pin_messages'),
                'can_manage_topics': admin.get('can_manage_topics'),
                'can_delete_messages': admin.get('can_delete_messages'),
            })
PY
```

Hermes-side evidence search:

```bash
# Look for actual Telegram pin/topic operations in Hermes logs.
journalctl --user -u hermes-gateway --since '24 hours ago' --no-pager \
  | grep -Ei 'pin|pinned|topic|forum|edit_forum_topic|rename' || true

# Search local rotated gateway logs if journal retention is not enough.
grep -RniE 'pin|pinned|topic|forum|edit_forum_topic|rename' /home/ubuntu/.hermes/logs/gateway.log* 2>/dev/null || true
```

## Interpreting pinned topic service messages

In Telegram forum supergroups, a pinned banner can point to a service message, not normal text. For example, `getChat.pinned_message` may show:

- `text: null`
- `forum_topic_edited: {'name': '<topic name>'}`
- `from: <human admin>`
- `message_thread_id: <topic id>`

That means the pinned item is a Telegram service message such as:

`Ayman renamed the topic to Pos Systems`

Do not call this a hacker or virus without evidence. Explain that Telegram may be preserving or redisplaying the pinned-service-message state even after the visible message is deleted. Deleting the service message is not the same as clearing the chat's pinned-message pointer.

## Hermes auto topic rename/pin distinction

Hermes has topic-related behavior, but it is specific:

- Topic title auto-rename can happen for Telegram DM topic lanes when Hermes generates a session title.
- It can be disabled with `gateway.platforms.telegram.extra.disable_topic_auto_rename`.
- Hermes may pin a managed `System` intro message when enabling Telegram DM topic mode.
- Those are different from a forum supergroup pinned service message created by a human topic rename.

When evidence shows `from` is a human admin and `forum_topic_edited` is set, report it as Telegram/forum-topic state unless Hermes logs show a matching pin call.

## Write actions require approval

These mutate the Telegram group/topic and require explicit user approval:

- `unpinChatMessage`
- `unpinAllChatMessages`
- `editForumTopic`
- changing bot admin rights
- deleting messages
- disabling Hermes topic auto-rename or changing gateway config
- restarting Hermes gateway

## Safe unpin after approval

If the user approves unpinning a specific message:

```bash
python3 - <<'PY'
import os, json, urllib.request, urllib.parse, pathlib
for env_path in [pathlib.Path('/home/ubuntu/.hermes/.env')]:
    if env_path.exists():
        for line in env_path.read_text(errors='ignore').splitlines():
            if line.strip().startswith('TELEGRAM_BOT_TOKEN='):
                os.environ['TELEGRAM_BOT_TOKEN'] = line.split('=', 1)[1].strip().strip('"\'')
                break

token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = '<chat_id_here>'
message_id = '<message_id_here>'
if not token:
    raise SystemExit('TELEGRAM_BOT_TOKEN missing')
base = f'https://api.telegram.org/bot{token}/'
url = base + 'unpinChatMessage?' + urllib.parse.urlencode({
    'chat_id': chat_id,
    'message_id': message_id,
})
with urllib.request.urlopen(url, timeout=20) as r:
    print(json.load(r))
PY
```

Then verify with `getChat` again. If `pinned_message` is absent or different, report success. If it returns, tell the user to inspect Telegram `Manage Group -> Recent Actions` for an admin/bot re-pinning action, because Bot API does not expose full admin action history.

## Reporting pattern

Use incident language without feeding panic:

- `System report: this is a Telegram service-message pin, not evidence of malware.`
- `Verified: pinned_message.message_id=<id>, thread=<thread>, from=<human/bot>, type=<forum_topic_edited/text/etc>.`
- `Hermes evidence: no matching pin call found in logs.`
- `Next move: unpin, not delete. Approval required.`

## Common System Alerts

- `pinned_message.text is None`: likely a service message; inspect `forum_topic_created`, `forum_topic_edited`, or nested `pinned_message`.
- User deletes or dismisses pinned banner and it returns: explain that the Telegram `X` may only hide the banner locally; verify server state with `getChat.pinned_message` before claiming it is cleared.
- `unpinChatMessage` says `service messages can't be pinned`: Telegram can report a service message as pinned while refusing exact unpin. Escalate to topic/group unpin only with approval; if the same service message returns, delete the underlying service message after explicit approval.
- Bot cannot unpin: verify bot admin rights include `can_pin_messages` and the chat is the correct supergroup/forum.
- Topic keeps renaming: inspect Hermes topic auto-rename settings and Telegram Recent Actions; disable auto-rename only after approval.
