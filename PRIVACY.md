# Privacy Policy for Repository Contributions

This repository is intended to contain only information required to build, test, document, and maintain the public open-source project.

## Prohibited information

Do not commit or publish:

- employer, client, internal organization, or non-public team identifiers;
- automated assistant, internal tool, or corporate attribution trailers;
- private or corporate email addresses unless the owner explicitly chooses to publish them;
- local usernames, home directories, hostnames, device identifiers, or internal filesystem paths;
- credentials, access tokens, cookies, private keys, host definitions, terminal history, or private configuration;
- proprietary binaries, private source code, internal documentation, or confidential data;
- generated app bundles, signing artifacts, crash reports, or build logs containing local metadata.

Use a GitHub-provided noreply address for commits unless you intentionally want another address to be public.

## Publication checklist

Before every push, tag, or release:

1. Run `scripts/privacy-audit.sh`.
2. Inspect raw commit messages and author metadata.
3. Review all tracked files, tags, release notes, and generated artifacts.
4. Confirm that dependency licenses and notices remain accurate.
5. Confirm that no ignored local files are staged.

If prohibited data is published, stop further publication, remove all reachable references, rotate any exposed credential, and follow the hosting provider's sensitive-data removal guidance.
