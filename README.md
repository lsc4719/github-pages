# Reports on GitHub Pages

이 저장소는 공개 HTML 보고서를 GitHub Pages로 제공합니다. 저장소와 게시된 파일은 누구나 볼 수 있으므로 비공개 정보는 넣지 않습니다.

- 보고서 목록: https://lsc4719.github.io/github-pages/
- 예시 보고서: https://lsc4719.github.io/github-pages/reports/spring-start-here-chapter-7/

## 구조

```text
index.html                         # 사이트 홈: 보고서 카드와 링크
reports.json                       # 보고서 메타데이터 목록
reports/
  spring-start-here-chapter-7/
    index.html                     # 개별 보고서
.github/workflows/pages.yml        # GitHub Pages 배포 워크플로
.nojekyll                          # 정적 파일을 그대로 제공
```

각 보고서는 `reports/<slug>/index.html`에 놓습니다. 예를 들어 `reports/my-report/index.html`은 `https://lsc4719.github.io/github-pages/reports/my-report/`에서 열립니다. 이미지나 CSS 등 보고서 전용 파일은 해당 디렉터리에 함께 두고 상대 경로로 연결합니다.

## 새 보고서 추가하기

1. `reports/` 아래에 영문 소문자와 하이픈으로 된 고유한 디렉터리를 만들고 그 안에 `index.html`을 작성합니다.
2. 루트 `index.html`의 `<section class="grid">` 안에 기존 `article.report-card`를 참고해 날짜, 제목, 요약과 `./reports/<slug>/` 링크를 추가합니다. 제목과 Open report 링크를 모두 새 경로로 바꿉니다.
3. `reports.json`의 `reports` 배열에도 `slug`, `title`, `summary`, `date` (`YYYY-MM-DD`), `path` (`./reports/<slug>/`)를 추가합니다. JSON 문법과 쉼표를 확인합니다.
4. 로컬에서 저장소 루트를 기준으로 `python3 -m http.server 8000`을 실행하고 `http://localhost:8000/`에서 목록과 보고서 링크, 이미지 및 스타일을 확인합니다. 종료하려면 `Ctrl+C`를 누릅니다.
5. 변경 파일을 커밋하고 `main` 브랜치에 푸시합니다. GitHub Actions의 **Deploy GitHub Pages** 워크플로가 자동 배포합니다. Actions 탭에서 성공을 확인한 후 공개 목록과 보고서 URL을 열어 확인합니다. 필요하면 Actions에서 워크플로를 수동 실행할 수도 있습니다.

`reports.json`은 메타데이터 파일이며 현재 홈 페이지가 이를 자동으로 읽지는 않습니다. 따라서 목록에 표시하려면 `index.html` 카드도 직접 추가해야 합니다. GitHub Pages는 저장소 이름이 포함된 `/github-pages/` 아래에서 제공되므로 사이트 루트(`/reports/...`) 대신 상대 경로를 사용합니다.
