## Google Cloud credits are provided for this project `#VertexAISprint`
Thanks, [Google](https://github.com/google) :)

# Gemini AI Code Reviewer

A GitHub Action that automatically reviews pull requests using Google's Gemini AI.

## Features

- Review your PRs using Gemini API
- Give comments and suggestions to improve the source codes
- **🆕 Code Suggestions**: Not just comments, but actual code recommendations with before/after examples
- **Two trigger modes**: Comment trigger (`/gemini-review`) and manual button trigger
- Flexible model selection and file exclusion patterns
- Support for multiple review modes (Standard, Strict, Lenient, Security-focused, Performance-focused)
- GitHub-compatible comment formatting with code suggestion blocks

![Demo](assets/img/Demo.png)
![Demo2](assets/img/Demo2.png)
[Video Demo](https://www.youtube.com/watch?v=pc1ffEFMIQo)

## Setup

1. To use this GitHub Action, you need an Gemini API key. If you don't have one, sign up for an API key
   at [Google AI Studio](https://makersuite.google.com/app/apikey).

2. Add the Gemini API key as a GitHub Secret in your repository with the name `GEMINI_API_KEY`. You can find more
   information about GitHub Secrets [here](https://docs.github.com/en/actions/reference/encrypted-secrets).

3. Create a `.github/workflows/code-review.yml` file in your repository and add the following content:

```yaml
name: Gemini AI Code Reviewer

on:
  issue_comment:
    types: [created]

permissions: write-all

jobs:
  gemini-code-review:
    runs-on: ubuntu-latest
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '/gemini-review')
    steps:
      - name: PR Info
        run: |
          echo "Comment: ${{ github.event.comment.body }}"
          echo "Issue Number: ${{ github.event.issue.number }}"
          echo "Repository: ${{ github.repository }}"

      - name: Checkout Repo
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Get PR Details
        id: pr
        run: |
          PR_JSON=$(gh api repos/${{ github.repository }}/pulls/${{ github.event.issue.number }})
          echo "head_sha=$(echo $PR_JSON | jq -r .head.sha)" >> $GITHUB_OUTPUT
          echo "base_sha=$(echo $PR_JSON | jq -r .base.sha)" >> $GITHUB_OUTPUT
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - uses: seungheeMa/gemini-code-reviewer@main
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GEMINI_MODEL: gemini-2.5-pro # Optional, default is `gemini-2.5-flash`
          EXCLUDE: "*.md,*.txt,package-lock.json,*.yml,*.yaml"
```
> if you don't set `GEMINI_MODEL`, the default model is `gemini-2.5-flash`. `gemini-2.5-flash` is a next-generation model offering speed and multimodal generation capabilities.  It's suitable for a wide variety of tasks, including code generation, data extraction, and text editing.. For the detailed information about the models, please refer to [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini).
4. Commit codes to your repository, and working on your pull requests.
5. When you're ready to review the PR, you can trigger the workflow in two ways:

   **Option 1: Comment Trigger (Original Method)**
   - Comment `/gemini-review` in the PR to trigger the review

   **Option 2: Manual Button Trigger (New Feature)**
   - Go to the **Actions** tab in your repository
   - Select **Manual Gemini AI Code Reviewer** workflow
   - Click **Run workflow** and enter the PR number and other options
   - Click **Start workflow** to begin the review

   For detailed instructions on the manual trigger, see [MANUAL_TRIGGER_GUIDE.md](MANUAL_TRIGGER_GUIDE.md).

## How It Works

This GitHub Action uses the Gemini AI API to provide code review feedback. It works by:

1. **Analyzing the changes**: It grabs the code modifications from your pull request and filters out any files you don't want reviewed.
2. **Consulting the Gemini model**: It sends chunks of the modified code to the Gemini for analysis.
3. **Providing feedback**: Gemini AI examines the code and generates review comments **with actual code suggestions**.
4. **Delivering the review**: The Action adds the comments directly to your pull request on GitHub with formatted code suggestion blocks.

## 🆕 Code Suggestions Feature

The enhanced code reviewer now provides **actual code recommendations** instead of just textual comments:

### Example Output

```markdown
보안 취약점: 사용자 입력을 직접 SQL 쿼리에 사용하고 있습니다. SQL 인젝션 공격에 취약합니다.

### 💡 코드 제안:

**제안 1:** PreparedStatement를 사용하여 SQL 인젝션을 방지합니다.
```diff
-query = "SELECT * FROM users WHERE id = " + userInput;
---
+query = "SELECT * FROM users WHERE id = ?";
+stmt = conn.prepareStatement(query);
+stmt.setString(1, userInput);
```
```

### Features

- **Before/After Code**: Shows exactly what to change and how
- **Multiple Suggestions**: Can provide multiple alternative solutions
- **Explanations**: Each suggestion includes detailed reasoning
- **GitHub Compatible**: Uses GitHub's suggestion format for easy application
- **Language Agnostic**: Works with any programming language

### Configuration Options

You can customize the review behavior using environment variables:

```yaml
- uses: seungheeMa/gemini-code-reviewer@main
  with:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    REVIEW_MODE: standard  # Options: standard, strict, lenient, security_focused, performance_focused
    EXCLUDE: "*.md,*.txt,package-lock.json,*.yml,*.yaml"
    MAX_FILES_PER_REVIEW: 50
    MAX_LINES_PER_HUNK: 500
```

### Review Modes

- **Standard**: Balanced review focusing on bugs, security, and performance
- **Strict**: Thorough review including minor style issues
- **Lenient**: Only critical bugs and security vulnerabilities
- **Security-focused**: Exclusively security vulnerabilities
- **Performance-focused**: Exclusively performance issues

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Star History ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=seungheeMa/gemini-code-reviewer&type=Date)](https://star-history.com/#seungheeMa/gemini-code-reviewer&Date)
