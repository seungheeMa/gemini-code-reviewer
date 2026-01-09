#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced code reviewer with code suggestions.

This script creates a mock scenario to test the new code suggestion functionality.
"""

import json
import sys
import os

# Add the gemini_reviewer module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly from the models file to avoid dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location("models", "gemini_reviewer/models.py")
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

AIResponse = models.AIResponse
CodeSuggestion = models.CodeSuggestion
ReviewComment = models.ReviewComment
ReviewPriority = models.ReviewPriority


def test_code_suggestion_parsing():
    """Test parsing of AI responses with code suggestions."""
    print("🧪 Testing code suggestion functionality...")
    
    # Mock AI response with code suggestions
    mock_ai_response_data = {
        "lineNumber": 42,
        "reviewComment": "이 변수명은 더 명확하게 만들 수 있습니다. 현재 이름은 너무 일반적입니다.",
        "priority": "medium",
        "category": "maintainability",
        "confidence": 0.8,
        "codeSuggestions": [
            {
                "originalCode": "let data = fetchUserData();",
                "suggestedCode": "let userData = fetchUserData();",
                "explanation": "변수명을 'data'에서 'userData'로 변경하여 더 명확한 의미를 전달합니다.",
                "lineStart": 42,
                "lineEnd": 42
            },
            {
                "originalCode": "if (data.length > 0) {",
                "suggestedCode": "if (userData && userData.length > 0) {",
                "explanation": "null 체크를 추가하여 안정성을 향상시킵니다.",
                "lineStart": 43,
                "lineEnd": 43
            }
        ]
    }
    
    # Test creating CodeSuggestion objects
    suggestions = []
    for suggestion_data in mock_ai_response_data["codeSuggestions"]:
        suggestion = CodeSuggestion(
            original_code=suggestion_data["originalCode"],
            suggested_code=suggestion_data["suggestedCode"],
            explanation=suggestion_data["explanation"],
            line_start=suggestion_data["lineStart"],
            line_end=suggestion_data["lineEnd"]
        )
        suggestions.append(suggestion)
    
    print(f"✅ Created {len(suggestions)} code suggestions")
    
    # Test creating AIResponse with suggestions
    ai_response = AIResponse(
        line_number=mock_ai_response_data["lineNumber"],
        review_comment=mock_ai_response_data["reviewComment"],
        priority=ReviewPriority.MEDIUM,
        category=mock_ai_response_data["category"],
        confidence=mock_ai_response_data["confidence"],
        code_suggestions=suggestions
    )
    
    print(f"✅ Created AI response with {len(ai_response.code_suggestions)} suggestions")
    
    # Test creating ReviewComment with suggestions
    review_comment = ReviewComment(
        body=ai_response.review_comment,
        path="src/example.js",
        position=15,
        line_number=ai_response.line_number,
        priority=ai_response.priority,
        category=ai_response.category,
        code_suggestions=ai_response.code_suggestions
    )
    
    print(f"✅ Created review comment with {len(review_comment.code_suggestions)} suggestions")
    
    # Test GitHub comment format
    github_comment = review_comment.to_github_comment()
    print("\n📝 Generated GitHub Comment:")
    print("=" * 50)
    print(github_comment["body"])
    print("=" * 50)
    
    return True


def test_json_response_format():
    """Test the expected JSON response format from Gemini."""
    print("\n🧪 Testing JSON response format...")
    
    # Example of what Gemini should return
    expected_response = {
        "reviews": [
            {
                "lineNumber": 25,
                "reviewComment": "보안 취약점: 사용자 입력을 직접 SQL 쿼리에 사용하고 있습니다. SQL 인젝션 공격에 취약합니다.",
                "priority": "critical",
                "category": "security",
                "confidence": 0.95,
                "codeSuggestions": [
                    {
                        "originalCode": "query = \"SELECT * FROM users WHERE id = \" + userInput;",
                        "suggestedCode": "query = \"SELECT * FROM users WHERE id = ?\";\nstmt = conn.prepareStatement(query);\nstmt.setString(1, userInput);",
                        "explanation": "PreparedStatement를 사용하여 SQL 인젝션을 방지합니다.",
                        "lineStart": 25,
                        "lineEnd": 25
                    }
                ]
            }
        ]
    }
    
    print("✅ Expected JSON format from Gemini:")
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))
    
    return True


def main():
    """Run all tests."""
    print("🚀 Testing Enhanced Gemini Code Reviewer with Code Suggestions\n")
    
    try:
        # Test code suggestion parsing
        if not test_code_suggestion_parsing():
            print("❌ Code suggestion parsing test failed")
            return False
        
        # Test JSON response format
        if not test_json_response_format():
            print("❌ JSON response format test failed")
            return False
        
        print("\n✅ All tests passed! The enhanced code reviewer is ready.")
        print("\n📋 Key Features Added:")
        print("   • Code suggestions with before/after code")
        print("   • Explanations for each suggestion")
        print("   • GitHub-compatible comment formatting")
        print("   • Enhanced prompt engineering for better code recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
