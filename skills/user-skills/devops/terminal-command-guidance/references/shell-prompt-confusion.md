# Shell prompt confusion and blank output pattern

## Context

A user wanted to read `~/.hermes/SOUL.md`. The assistant suggested commands like `cat ~/.hermes/SOUL.md`, but the user reported that it showed nothing. Their pasted transcript showed they were typing wrapper words such as `bash` and `sh` before the actual commands:

```text
ubuntu@instance:~$ bash
    cat ~/.hermes/SOUL.md
ubuntu@instance:~$ sh
    whoami
    echo "$HOME"
    ...
$ gfn
sh: 1: gfn: not found
```

The important observation was the prompt change from `ubuntu@host:~$` to `$`, meaning the user had entered a nested shell. They also typed `gfn`, causing a normal `command not found` error unrelated to the original file-reading task.

## Durable lesson

When a user appears to paste commands incorrectly:

1. Stop giving multi-line command blocks.
2. Tell them explicitly not to type `bash` or `sh` unless starting a shell is the actual goal.
3. Ask them to run `exit` if the prompt changed to `$` and they are in a nested shell.
4. Continue with one single read-only command at a time.
5. Prefer absolute paths during diagnosis.
6. Use an output sentinel such as `echo '<<< END'` to distinguish empty file contents from swallowed terminal output.

## Good response shape

```text
You are inside an extra shell. First run:

exit

When you are back at `ubuntu@host:~$`, paste only this command:

nl -ba /home/ubuntu/.hermes/SOUL.md
```

## Minimal command sequence

```sh
printf 'TEST_OUTPUT_WORKS\n'
whoami
printf 'HOME=%s\nHERMES_HOME=%s\nPWD=%s\n' "$HOME" "${HERMES_HOME:-}" "$PWD"
stat /home/ubuntu/.hermes/SOUL.md
nl -ba /home/ubuntu/.hermes/SOUL.md
cat /home/ubuntu/.hermes/SOUL.md; echo '<<< END OF SOUL FILE'
```

If `cat` appears blank but `stat`/`wc -c` show bytes, inspect raw bytes:

```sh
xxd /home/ubuntu/.hermes/SOUL.md | head
```

## What not to persist

Do not save this as "cat does not work" or "shell is broken". The issue is command-entry confusion, not a durable system failure.
