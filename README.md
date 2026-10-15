# Kumar Sambhav — AI engineering portfolio

A static HTML, CSS, and JavaScript portfolio, with automated checks and GitHub Pages publishing. The current design, photograph, case studies, and resume PDF are included.

The source of truth is [Kumar-sambhav04/my_portfolio_repository](https://github.com/Kumar-sambhav04/my_portfolio_repository). See docs/PUBLISHING.md for activation and cutover. A successful **Verify live deployment** run confirms that the published address serves the expected version.

## How future edits work

Ask ChatGPT to update this repository. It fetches the latest source, makes the requested change on a branch, runs checks, and opens a pull request. When publication is authorized, merging into main triggers deployment. The workflow verifies that the live website serves the expected commit and files. The same URL serves later updates.

GitHub is the source of truth after migration. A new chat can resume from the repository and its AGENTS.md; continuity does not depend on retaining this conversation's temporary files. The GitHub integration must be connected and authorized for this repository, and publishing actions need the relevant write capability.

## Files to edit

| File | Purpose |
| --- | --- |
| dist/index.html | Page content, navigation, experience, tools, and contact links |
| dist/styles.css | Layout, colors, spacing, and responsive behavior |
| dist/app.js | Case studies, architecture tabs, mobile navigation, and email copy |
| dist/assets/kumar-sambhav.jpg | Original supplied portrait |
| dist/assets/kumar-sambhav-resume.pdf | Public downloadable resume |
| site.json | Intended production address for local/PR builds |
| .github/workflows/portfolio.yml | Validation, publishing, and live verification |

## Run the checks

Python 3.10+ and Node.js are sufficient. No application packages, API keys, paid server, or database are required.

```sh
python -m unittest discover -s tests -v
python scripts/check_site.py dist --javascript
python scripts/build_site.py
```

The checks detect missing local assets, broken navigation anchors, invalid markup references, duplicate IDs, missing image alt attributes, missing metadata, invalid PDF headers, and unsafe publish-directory contents. The build creates _site/, sets canonical/social metadata, and generates a sitemap and a file-hash manifest. Only _site/ is uploaded to Pages.

These checks do not prove visual quality, accessibility conformance, or whether an external LinkedIn/GitHub link still works. Review layout and changed interactions before publishing. The deployed-file check establishes file availability and identity, not browser rendering.

For a local visual preview, run `python -m http.server 8000 --directory _site` and open http://localhost:8000. Stop the server when finished.

## Updates and rollback

Changes go through a pull request and the Validate portfolio check. Review the changes in the conversation before merging; branch protection is optional for this personal repository. Existing live content stays available while a proposed change is checked. A failed pre-deployment check prevents that workflow from publishing. If the final live verification fails, investigate the deployment; automatic rollback is deliberately not attempted. To restore an earlier version, revert the unwanted change, run checks, and merge the revert. See docs/PUBLISHING.md.

Dependabot opens weekly pull requests for GitHub Actions updates. Review them through the same checks. Keep the account and repository available and avoid renaming the repository, changing the GitHub username, or disabling Pages without planning a URL migration.

## Future-edit prompt

> Update my portfolio in Kumar-sambhav04/my_portfolio_repository. Read AGENTS.md, fetch the latest main, and [describe changes]. Preserve the current design and unrelated content. Run the checks, show the result, and publish when authorized by my request. Confirm the deployed commit and live URL.

## References

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

The original ChatGPT Sites version is an existing published copy. This GitHub package intentionally excludes that platform's project identity, repository credentials, and deployment configuration.
