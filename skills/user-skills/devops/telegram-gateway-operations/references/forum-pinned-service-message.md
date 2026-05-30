# Telegram forum pinned service-message incident pattern

## Trigger

Use this reference when a Telegram group/forum topic shows a pinned banner such as `Ayman renamed the topic to POS systems`, and the user says deleting it makes it return.

## Read-only evidence to collect

- `getChat` for the supergroup/forum `chat_id`.
- `getChatAdministrators` to confirm which admins/bots can pin and manage topics.
- Hermes gateway logs for `pin`, `pinned`, `topic`, `forum`, `edit_forum_topic`, and `rename`.
- Cron jobs / scheduled deliveries if the suspicion is recurring automation.

## Key Bot API shape

If `getChat.result.pinned_message` looks like this:

```text
message_id: <id>
message_thread_id: <topic id>
from: <human admin>
text: None
forum_topic_edited: {'name': '<topic name>'}
```

then the pinned item is a Telegram service message for topic edit/rename, not a normal Hermes text response.

## Interpretation

- Do not call it a virus/hacker by default.
- Do not assume Hermes pinned it merely because the Hermes bot is an admin.
- The `X` on Telegram's pinned banner may only dismiss/hide the banner locally; it is not proof the server-side pin was removed.
- Deleting or hiding the visible service banner may not clear Telegram's pinned-message pointer.
- First try the least-broad real server-side unpin (`unpinChatMessage`) after approval, but be aware Telegram may reject service messages with `Bad Request: service messages can't be pinned` even while `getChat` reports that service message as pinned.

## Safe response

Report plainly:

```text
Telegram says the pinned item is message <id> in topic <thread>, created by <from>, type forum_topic_edited. That is the service message for the topic rename, not normal text. I found/no found Hermes log evidence of a pin call. Next move is to unpin message <id>; approval required because it mutates the group.
```

## If unpin fails or returns

Escalate carefully, with approval for each broader/destructive step:

1. `unpinChatMessage(chat_id, message_id)` for the exact reported pinned message.
2. For forum topics, try `unpinAllForumTopicMessages(chat_id, message_thread_id)` if available. If Telegram returns repeated `Too Many Requests: retry after 3` despite respecting the cooldown, do not spin forever.
3. `unpinAllChatMessages(chat_id)` can clear the `getChat.pinned_message` pointer but is broader and may remove all group pins; require explicit approval. Verify immediately, then verify again after the user re-enters/restarts the Telegram client if they still see the banner — in the observed incident `getChat.pinned_message` temporarily returned `None` after group-level unpin, then later returned to the same service message.
4. If `getChat.pinned_message` later returns to the same service message and no Hermes/webhook evidence exists, delete the underlying service message itself (`deleteMessage(chat_id, message_id)`) only after explicit approval. In the observed incident, manual deletion of the topic-rename service message was the final fix.

## If it comes back after unpin or deletion

Ask the user to inspect Telegram `Manage Group -> Recent Actions` for who pinned or changed topic info. Bot API does not provide the full recent-actions audit log. Also check bot webhook state and pending updates when compromise is suspected, but avoid alarmism unless the evidence shows an external actor.
