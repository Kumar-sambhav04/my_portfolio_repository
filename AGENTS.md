# Portfolio maintenance

This repository is the source of truth for Kumar Sambhav's portfolio. The intended GitHub repository is `Kumar-sambhav04/my_portfolio_repository`. Confirm the actual connected owner and repository before writing. Read README.md and docs/PUBLISHING.md when resuming work.

## Workflow

- Fetch the latest default branch before every change. Do not depend on files from an old chat workspace.
- Create a short-lived branch and a pull request. Preserve unrelated work.
- Edit source files in dist/. Never edit generated _site/ files.
- Run the checks in README.md. A green static check does not establish visual correctness. Inspect responsive layouts and interactions using available approved browser tools for layout changes; state any verification limitation.
- Use the user's request and current authorization to decide when to merge and publish. When publishing is authorized, merge the checked pull request; do not ask for approval already given. For draft/review-only requests, leave the pull request open.
- Publish through the GitHub Actions workflow from main. Do not manually upload a separate version or also publish edits to the old ChatGPT Sites copy.
- Confirm the successful live-deployment verification for the actual commit before reporting the update as live.
- Roll back by reverting the unwanted change in a new checked pull request. Do not force-push, reset shared history, delete the repository, or silently overwrite an existing site.

## Content accuracy and design

- Preserve the professional warm-white, slate, and muted-teal design unless a redesign is requested.
- Kumar is transitioning from data/business analysis to applied AI engineering. Do not describe his analyst experience as years of professional AI engineering.
- EHE Data System: founding team member; data/business analysis from December 2022. His principal AWS Glue client-project contributions were data validation and Power BI dashboarding, with collaboration across other tasks. Do not claim sole ETL ownership.
- Independent projects and employment must remain clearly distinguished. Do not invent measured outcomes, clients, credentials, tool proficiency, repository URLs, or live demos.
- Keep the RGD Tech architecture graphic in the Corrective Hybrid RAG project section. Do not restore the removed tools strip below the profile.
- The approved ML/DL group is scikit-learn, TensorFlow, PyTorch, and ML/DL Fundamentals. Jev belongs in AI application tools. Preserve approved spelling unless the user changes it.
- Preserve supplied photo and contact links. Update project/resume links when verified replacements are available.
- The public website and repository must contain only public portfolio assets; credentials and local environment files do not belong in dist/.

## Stable address and migration

site.json records the intended address; the production workflow uses GitHub Pages' actual configured address when packaging the site. GitHub account/repository names and custom-domain settings determine the live URL. Do not rename them casually.

After the first verified GitHub deployment, update the editable resume and its downloadable PDF to the actual live address. Keep the old ChatGPT Sites URL available for previously shared resumes, but treat it as an archived copy unless explicitly asked to update it.
