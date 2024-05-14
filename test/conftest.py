# conftest.py
import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # 이 훅은 각 테스트 실행 결과를 처리합니다.
    outcome = yield
    rep = outcome.get_result()

    # 테스트가 끝난 후 call 단계에서 커스텀 메시지를 추가합니다.
    if rep.when == 'call':
        describe_marker = item.get_closest_marker("describe")
        if describe_marker:
            describe = describe_marker.args[0]
            rep.describe = describe  # 사용자 정의 속성으로 메시지 저장

@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    # 커스텀 메시지가 있는 경우 이를 사용합니다.
    describe = getattr(report, 'describe', report.nodeid)

    # 각 테스트의 상태에 따라 결과를 포맷합니다.
    if report.when == 'call':
        if report.passed:
            return (report.outcome, 'PASS', f"{describe} ✅ PASSED ")
        elif report.failed:
            return (report.outcome, 'FAIL', f"{describe} ❌ FAILED ")
    elif report.skipped:
        return (report.outcome, 'SKIP', f"{describe} ➖ SKIPPED ")
