#!/usr/bin/env python3
"""
Gemini AI Code Reviewer - Main Entry Point

A GitHub Action that automatically reviews pull requests using Google's Gemini AI.
This is the main entry point that orchestrates the entire review process.
"""

import asyncio
import logging
import logging.handlers
import os
import sys
from typing import Optional

from gemini_reviewer import Config, CodeReviewer, CodeReviewerError, ReviewResult


def setup_logging_from_config(config: Config):
    """Set up logging based on configuration."""
    log_handlers = [logging.StreamHandler(sys.stdout)]
    
    # Add file handler if enabled
    if config.logging.enable_file_logging:
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                config.logging.log_file_path,
                maxBytes=config.logging.max_log_size,
                backupCount=config.logging.backup_count
            )
            log_handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
    
    logging.basicConfig(
        level=getattr(logging, config.logging.level.value),
        format=config.logging.format,
        handlers=log_handlers
    )
    
    # Set specific log levels for external libraries
    logging.getLogger('github').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)


def validate_environment() -> bool:
    """Validate that all required environment variables are present."""
    required_vars = ["GITHUB_TOKEN", "GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"오류: 필수 환경 변수 누락: {', '.join(missing_vars)}")
        return False
    
    # Check if this is a manual trigger
    is_manual = os.environ.get("MANUAL_TRIGGER", "").lower() == "true"
    
    if is_manual:
        # For manual trigger, validate PR number
        if not os.environ.get("PR_NUMBER"):
            print("오류: 수동 트리거 모드에서는 PR_NUMBER 환경 변수가 필요합니다.")
            return False
    else:
        # For comment trigger, validate event path and name
        if not os.environ.get("GITHUB_EVENT_PATH"):
            print("오류: GITHUB_EVENT_PATH 환경 변수 누락")
            return False
        
        event_name = os.environ.get("GITHUB_EVENT_NAME", "")
        if event_name != "issue_comment":
            print(f"오류: 지원되지 않는 GitHub 이벤트: {event_name}. 'issue_comment'만 지원됩니다.")
            return False
    
    return True


def check_if_comment_trigger() -> bool:
    """Check if this was triggered by a comment with the review command."""
    import json
    
    try:
        with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
            event_data = json.load(f)
        
        # Check if it's a comment on a PR
        if not event_data.get("issue", {}).get("pull_request"):
            print("정보: 댓글이 Pull Request에 있지 않아 리뷰를 건너뜁니다.")
            return False
        
        # Check if comment contains the review trigger
        comment_body = event_data.get("comment", {}).get("body", "").lower()
        if "/gemini-review" not in comment_body:
            print("정보: 댓글에 '/gemini-review' 트리거가 없어 리뷰를 건너뜁니다.")
            return False
        
        return True
        
    except Exception as e:
        print(f"오류: GitHub 이벤트 데이터를 처리할 수 없습니다: {e}")
        return False


async def create_manual_event_data(pr_number: str) -> str:
    """Create mock event data for manual trigger."""
    import json
    import tempfile
    
    # Create mock event data that mimics a comment trigger
    mock_event = {
        "issue": {
            "number": int(pr_number),
            "pull_request": {}  # Just indicate it's a PR
        },
        "comment": {
            "body": "/gemini-review",
            "user": {
                "login": "manual-trigger"
            }
        },
        "repository": {
            "name": os.environ.get("GITHUB_REPOSITORY", "").split("/")[-1] if os.environ.get("GITHUB_REPOSITORY") else "unknown",
            "owner": {
                "login": os.environ.get("GITHUB_REPOSITORY", "").split("/")[0] if os.environ.get("GITHUB_REPOSITORY") else "unknown"
            }
        }
    }
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_event, f, indent=2)
        return f.name


async def main_async() -> int:
    """Main async function for the code review process."""
    print("🤖 Gemini AI 코드 리뷰어 시작 중...")
    
    # Validate environment first
    if not validate_environment():
        return 1
    
    # Check if this is a manual trigger
    is_manual = os.environ.get("MANUAL_TRIGGER", "").lower() == "true"
    
    # For comment trigger, check if this is a valid trigger
    if not is_manual and not check_if_comment_trigger():
        return 0  # Not an error, just not our trigger
    
    try:
        # Load configuration from environment
        config = Config.from_environment()
        
        # Setup logging based on configuration
        setup_logging_from_config(config)
        logger = logging.getLogger(__name__)
        
        if is_manual:
            logger.info("=== Gemini AI 코드 리뷰어 시작 (수동 트리거) ===")
            pr_number = os.environ["PR_NUMBER"]
            logger.info(f"대상 PR: #{pr_number}")
        else:
            logger.info("=== Gemini AI 코드 리뷰어 시작 (댓글 트리거) ===")
        
        logger.info(f"설정 로드됨: {config.to_dict()}")
        
        # Create code reviewer with configuration
        with CodeReviewer(config) as reviewer:
            
            # Test connections to external services
            logger.info("외부 서비스 연결 테스트 중...")
            connections = reviewer.test_connections()
            
            failed_connections = [service for service, status in connections.items() if not status]
            if failed_connections:
                logger.error(f"연결 실패: {failed_connections}")
                return 1
            
            logger.info("✅ 모든 외부 서비스 연결이 정상 작동합니다")
            
            # Determine the event path for the review
            if is_manual:
                # For manual trigger, we need to create a mock event or use PR number directly
                event_path = await create_manual_event_data(pr_number)
            else:
                event_path = os.environ["GITHUB_EVENT_PATH"]
            
            # Perform the code review
            result = await reviewer.review_pull_request(event_path)
            
            # Log results
            await _log_review_results(result, reviewer)
            
            # Return appropriate exit code
            if result.errors:
                logger.error(f"리뷰 완료되었으나 {len(result.errors)}개 오류 발생")
                for error in result.errors:
                    logger.error(f"  - {error}")
                return 1
            else:
                logger.info("✅ 리뷰가 성공적으로 완료되었습니다")
                return 0
    
    except Exception as e:
        print(f"❌ 코드 리뷰 중 치명적 오류 발생: {str(e)}")
        logging.exception("Fatal error details:")
        return 1


async def _log_review_results(result: ReviewResult, reviewer: CodeReviewer):
    """Log comprehensive review results."""
    logger = logging.getLogger(__name__)
    
    # Basic results
    logger.info("=== 리뷰 결과 ===")
    logger.info(f"PR: #{result.pr_details.pull_number} - {result.pr_details.title}")
    logger.info(f"처리된 파일: {result.processed_files}")
    logger.info(f"생성된 코멘트: {result.total_comments}")
    processing_time = result.processing_time or 0.0
    logger.info(f"처리 시간: {processing_time:.2f}초")
    
    # Comment breakdown by priority
    if result.comments:
        priority_counts = result.comments_by_priority
        logger.info("우선순위별 코멘트 분류:")
        for priority, count in priority_counts.items():
            if count > 0:
                emoji = {"critical": "🚨", "high": "⚠️", "medium": "💡", "low": "ℹ️"}.get(priority.value, "📝")
                priority_korean = {"critical": "치명적", "high": "높음", "medium": "보통", "low": "낮음"}.get(priority.value, priority.value.title())
                logger.info(f"  {emoji} {priority_korean}: {count}")
    
    # Detailed statistics
    stats = reviewer.get_statistics()
    logger.debug("=== 상세 통계 ===")
    logger.debug(f"처리 통계: {stats.get('processing', {})}")
    logger.debug(f"GitHub 통계: {stats.get('github', {})}")
    logger.debug(f"Gemini 통계: {stats.get('gemini', {})}")
    logger.debug(f"파싱 통계: {stats.get('parsing', {})}")
    
    # Errors
    if result.errors:
        logger.warning(f"발생한 오류: {len(result.errors)}")
        for error in result.errors:
            logger.warning(f"  - {error}")


def main() -> int:
    """Main synchronous entry point."""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⚠️  사용자가 리뷰를 중단했습니다")
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"❌ 치명적 오류: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
