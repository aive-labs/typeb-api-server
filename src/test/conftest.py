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


# # DB 초기화
# @pytest.fixture(scope="session")
# def test_db():
#     metadata = MetaData()
#     db = Database('sqlite:///./test.db')
#     engine = db._engine
#     metadata.create_all(db._engine)

#     try:
#         yield engine
#     finally:
#         metadata.drop_all(engine)

# @pytest.fixture(scope="function")
# def test_session(test_db):
#     connection = test_db.connect()

#     trans = connection.begin()
#     session = sessionmaker()(bind=connection)

#     session.begin_nested()  # SAVEPOINT

#     @event.listens_for(session, "after_transaction_end")
#     def restart_savepoint(session, transaction):
#         """
#         Each time that SAVEPOINT ends, reopen it
#         """
#         if transaction.nested and not transaction._parent.nested:
#             session.begin_nested()

#     yield session

#     session.close()
#     trans.rollback()  # roll back to the SAVEPOINT
#     connection.close()
