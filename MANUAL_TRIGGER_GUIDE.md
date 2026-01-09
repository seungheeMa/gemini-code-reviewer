# Gemini AI Code Reviewer - Manual Trigger Guide

이 가이드는 Gemini AI Code Reviewer의 수동 트리거 기능을 사용하는 방법을 설명합니다.

## 개요

Gemini AI Code Reviewer는 이제 두 가지 방법으로 실행할 수 있습니다:

1. **댓글 트리거 (기존 방식)**: Pull Request에 `/gemini-review` 댓글을 달아 실행
2. **수동 트리거 (새로운 기능)**: GitHub Actions 탭에서 버튼 클릭으로 실행

## 수동 트리거 사용 방법

### 1. GitHub Actions 탭으로 이동

1. GitHub 저장소에서 **Actions** 탭을 클릭합니다
2. 왼쪽 메뉴에서 **Manual Gemini AI Code Reviewer** 워크플로우를 선택합니다

### 2. 워크플로우 실행

1. **Run workflow** 버튼을 클릭합니다
2. 다음 파라미터들을 입력합니다:

   - **Pull Request number**: 리뷰할 Pull Request 번호 (필수)
   - **Gemini model**: 사용할 Gemini 모델 선택 (선택사항, 기본값: gemini-3-flash-preview)
     - `gemini-3-flash-preview` (기본값)
     - `gemini-3-pro-preview` (기본값)
   - **Exclude patterns**: 제외할 파일 패턴 (선택사항, 쉼표로 구분)

3. **Start workflow** 버튼을 클릭하여 실행을 시작합니다

### 3. 실행 결과 확인

- 워크플로우 실행이 진행되며 로그를 실시간으로 확인할 수 있습니다
- 완료되면 리뷰 코멘트가 해당 Pull Request에 자동으로 추가됩니다

## 사용 예시

### 예시 1: 기본 사용
- Pull Request #42 리뷰
- 기본 Gemini 모델 사용
- 제외 파일 없음

```
Pull Request number: 42
Gemini model: gemini-3-flash-preview
Exclude patterns: (비워둠)
```

### 예시 2: 고급 사용
- Pull Request #123 리뷰
- 고급 모델 사용
- 테스트 파일과 설정 파일 제외

```
Pull Request number: 123
Gemini model: gemini-1.5-pro
Exclude patterns: *.test.js, *.config.js, package-lock.json
```

## 장점

### 수동 트리거의 장점

1. **간편한 실행**: 댓글을 달 필요 없이 버튼 클릭만으로 실행
2. **유연한 설정**: 실행할 때마다 모델과 제외 패턴을 다르게 설정 가능
3. **명시적인 실행**: 의도치 않은 실행을 방지
4. **실시간 모니터링**: GitHub Actions 인터페이스에서 실행 상태를 실시간으로 확인

### 댓글 트리거의 장점

1. **빠른 실행**: Pull Request 페이지에서 바로 실행 가능
2. **팀 협업**: 다른 팀원들이 쉽게 실행 요청 가능
3. **자동화**: 봇이나 스크립트를 통한 자동 실행 용이

## 권장 사용 시나리오

### 수동 트리거가 적합한 경우
- 정기적인 코드 리뷰 세션
- 특정 모델로 테스트하고 싶을 때
- 제외 파일 패턴을 동적으로 변경하고 싶을 때
- 리뷰 실행을 명확하게 제어하고 싶을 때

### 댓글 트리거가 적합한 경우
- 빠른 리뷰가 필요할 때
- 팀원들이 자유롭게 리뷰를 요청하게 하고 싶을 때
- CI/CD 파이프라인에 통합할 때

## 문제 해결

### 일반적인 문제들

1. **Pull Request 번호를 찾을 수 없음**
   - Pull Request 번호가 정확한지 확인
   - Pull Request가 같은 저장소에 있는지 확인

2. **권한 오류**
   - `GITHUB_TOKEN`과 `GEMINI_API_KEY` 시크릿이 올바르게 설정되었는지 확인
   - 워크플로우에 충분한 권한이 있는지 확인

3. **모델 실행 오류**
   - 선택한 Gemini 모델이 사용 가능한지 확인
   - API 키에 해당 모델 사용 권한이 있는지 확인

### 로그 확인 방법

1. GitHub Actions 탭에서 실행된 워크플로우를 클릭
2. 각 스텝을 확장하여 상세 로그 확인
3. 오류가 발생한 경우 로그의 오류 메시지를 참고하여 문제 해결

## 설정

### 필수 시크릿

다음 시크릿들이 저장소 설정에 있어야 합니다:

- `GITHUB_TOKEN`: GitHub API 접근 토큰
- `GEMINI_API_KEY`: Google Gemini API 키

### 권한 설정

워크플로우가 정상적으로 작동하려면 다음 권한이 필요합니다:

```yaml
permissions: write-all
```

## 기여

버그 리포트나 기능 요청은 GitHub Issues를 통해 제출해 주세요.
