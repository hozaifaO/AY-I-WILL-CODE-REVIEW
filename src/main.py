import logging
from src.github_client import GitHubClient, GitHubClientError
from src.openai_client import OpenAIClient, OpenAIClientError
from src.review_engine import ReviewEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    try:
        # Initialize the clients
        gh_client = GitHubClient()
        ai_client = OpenAIClient()
        review_engine = ReviewEngine(ai_client)

        # Get the PR diff
        if not (diff := gh_client.get_pr_diff()):
            raise GitHubClientError("No diff available for analysis")

        # Generate review with the AI engine
        raw_analysis = review_engine.generate_review(diff)
        findings = review_engine.parse_findings(raw_analysis)

        # Post the comments on the PR
        if findings:
            comment = "🔍 **AI Code Review Findings**\n\n" + "\n".join(
                f"**{f['severity']} {f['category']}**: {f['description']}\n"
                f"🛠️ *Suggested Fix*: {f['fix']}"
                for f in findings
            )
        else:
            comment = "✅ AI review completed - no significant issues found"

        if not gh_client.post_comment(comment):
            raise GitHubClientError("Failed to post review comments")

        logging.info("AI review completed successfully")

    except (GitHubClientError, OpenAIClientError) as e:
        logging.error(f"Review failed: {str(e)}")
        gh_client.post_comment("❌ AI review failed - check action logs")
        exit(1)

if __name__ == "__main__":
    main()