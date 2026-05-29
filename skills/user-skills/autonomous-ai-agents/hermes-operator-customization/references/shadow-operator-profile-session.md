# Shadow Operator Profile Session Lesson

## Context

The user provided a long "Shadow System Operator" persona and said to update the assistant's soul. The initial response saved a compact preference to memory but did not write the actual `~/.hermes/SOUL.md` file. The user later inspected the file and found only the default template. This caused frustration because the user expected the requested artifact to be changed.

The session then corrected the mistake by writing the full persona to:

```text
/home/ubuntu/.hermes/SOUL.md
```

and verifying it with a line count and header check.

The user later provided a long Operator Profile about Ayman Salmouni. That was saved separately as:

```text
/home/ubuntu/.hermes/OPERATOR_PROFILE.md
/home/ubuntu/.hermes/memories/USER.md
```

The Soul file was not changed during the Operator Profile update, and the assistant correctly stated that separation.

## Durable lesson

When the user says a document is meant to be a soul/profile/config, do not treat memory as the only persistence layer. Memory can summarize, but the actual file must be written if the request is for a file/config artifact.

## Correct pattern

1. Identify whether content is persona (`SOUL.md`) or user profile (`USER.md` / long profile doc).
2. Write the actual file when requested.
3. Verify with line count and first lines.
4. Report exactly which files changed and which files did not.

## Command-entry pitfall

The user accidentally prefixed commands with `bash` or `sh`, which opened a nested shell and made output confusing. For simple read commands, give one command at a time and explicitly say not to type `bash` or `sh` first.
