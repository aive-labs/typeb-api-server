# typeb api server

### commit
터미널에 git commit을 실행하면 자동으로 pre-commit git hook이 동작하게 됩니다.
참고로, pre-commit은 통해 자동으로 코드를 검사하고 수정하는 데 사용되는 도구이며 이를 활용해 코드 품질의 일관성을 유지할 수 있게 됩니다.
git에서 제공해주는 hook과 ruff에서 제공해주는 hook을 사용해 코드 품질을 유지합니다. 자동으로 코드를 수정을 해주고 수정된 파일은 git의 stage 상태에서 change 상태로 변경됩니다. 따라서 수정된 파일은 다시 stage 상태로 올려서 commit을 진행해야 합니다.

- .pre-commit-config.yaml (pre-commit 설정 파일)
- pyproject.toml (파이썬 lint 설정 파일)


### api server 실행
```bash
cd src
uvicorn main:app --reload
```


### test 코드 실행
```bash
cd src

# 전체 테스트 실행
python3 -m pytest -v -p no:warnings

# 특정 파일 테스트 실행
python3 -m pytest test/test_main.py -v -p no:warnings
```
