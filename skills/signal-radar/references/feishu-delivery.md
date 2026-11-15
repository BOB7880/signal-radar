# Feishu delivery through Lark CLI

1. Install the official CLI using the current instructions at https://github.com/larksuite/cli.
2. Run `lark-cli auth login --scope "im:message" --no-wait --json` and complete the browser/device authorization. If sending as the user requires `im:message.send_as_user`, grant that exact missing scope after reviewing the CLI response. Do not paste access tokens into chat or config files.
3. Select identity explicitly (`user` or `bot`) and target explicitly. Use `lark-cli im +chat-search --query "<chat name>" --as user` to locate a chat; inspect the resulting name and ID locally. For direct messages, `--user-id` requires a valid `ou_...` open_id. Do not guess IDs.
4. Set `FEISHU_CHAT_ID` and optionally `LARK_IDENTITY=user` in the local environment. The chat ID is destination configuration, not a credential; keep private chats private.
5. Preview with `python3 scripts/push_to_feishu.py reports/sample.md --dry-run`. Confirm the recipient, exact content, and sender identity before the first live send.
6. Send with `python3 scripts/push_to_feishu.py reports/sample.md`. It calls `lark-cli im +messages-send --markdown @<filename>`, uses the CLI's stored auth, captures output, and reports only a sanitized result. Nonzero exit or `{ "ok": false }` is failure. Never treat a dry run as delivery.

The CLI supports markdown posts and dry-run. Markdown rendering is not full CommonMark; test headings, tables, and links. For long reports, send a concise message plus a Feishu document/file link, or adapt the sender after checking current CLI help. This starter sends the Markdown body directly and does not create a Drive document.
