# Telegram Topic Command Center

## Purpose

Capture the reusable pattern for using one Telegram supergroup with many forum topics as separate Hermes command lanes.

Use this when Ayman wants to contact Hermes through multiple Telegram topics, route raid reports back to a topic, or bind different Skill Runes to different group topics.

## Core pattern

- Create one Telegram supergroup and enable Topics / forum mode.
- Add the Hermes bot to the group.
- Promote the bot to admin if it must manage topics or reliably send into all topics.
- Each Telegram topic has a distinct `message_thread_id`.
- Hermes preserves topic/thread context for forum messages, so each topic can act like a separate session lane.
- Holographic memory remains shared across lanes; short-term conversation/session context can differ by topic.

Example topic layout:

- General — normal General chat.
- Kanban Raids — task IDs, raid status, worker reports.
- System Ops — VPS, gateway, dashboard, systemd, logs.
- Memory Core — Holographic memory, daily curator, session recall.
- Research — web/model/tool research.
- Browser / Scrapy — browser-use and crawling jobs.
- Backups — backup and restore reports.
- Deployments — GitHub, CI/CD, deployments.

## Telegram privacy mode

Telegram bot privacy affects what Hermes receives inside groups:

- Privacy enabled: bot usually receives commands, mentions, and replies to the bot.
- Privacy disabled via BotFather `/setprivacy`: bot can receive normal group/topic messages.

For quieter operation, keep privacy enabled and use commands/mentions/replies. For a command-center feel where Ayman speaks naturally in every topic, disable privacy.

## Target syntax for topic delivery

A Telegram topic target has this shape:

```text
telegram:<chat_id>:<thread_id>
```

Example placeholder:

```text
telegram:-1001234567890:34567
```

Use this for cron deliveries, send_message targets, and any future automation that should report into a specific topic.

## Discovering chat_id and thread_id

Safe discovery sequence:

1. Create the group and topics.
2. Add/promote the bot.
3. In each topic, send `/status` or mention the bot.
4. Inspect Hermes session/source info, gateway logs, or session store to extract:
   - group `chat_id`
   - topic `thread_id`
   - topic name
5. Do not guess thread IDs; collect real values from live messages.

## Optional topic-specific Skill Rune binding

Hermes Telegram adapter supports group topic bindings via Telegram platform extra config (`group_topics`). Use only after real IDs are known.

Conceptual config shape:

```yaml
telegram:
  group_topics:
    - chat_id: "-100xxxxxxxxxx"
      topics:
        - name: "Kanban Raids"
          thread_id: "12345"
          skill: "shadow-mission-orchestration"
        - name: "System Ops"
          thread_id: "23456"
          skill: "terminal-command-guidance"
        - name: "Memory Core"
          thread_id: "34567"
          skill: "shadow-mission-orchestration"
```

Verify the actual config shape against the live Hermes version before editing, because platform config may be nested under adapter `extra` depending on setup.

## Operating doctrine

- Short requests: answer in the same topic.
- Missions likely to exceed 90 seconds: create Kanban cards, reply quickly with task IDs/status in the same topic, and keep the General free.
- Long-running worker output should return to the originating topic when possible.
- Use a dedicated `Kanban Raids` topic as the command room for cross-topic raid status if a mission spans multiple lanes.

## Pitfalls

- Topics organize lanes, but they do not by themselves make an inline long-running agent non-blocking. The Kanban-first rule still does that.
- Telegram bot privacy may make Hermes appear silent unless Ayman uses commands/mentions/replies.
- Do not configure topic bindings until real `chat_id` and `thread_id` values are collected.
- Forum group General topic may have special thread handling; verify delivery with a test message after configuring.
