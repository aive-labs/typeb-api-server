## Alembic 기본 명령어

수동으로 새로운 버전 생성

- 버전만 생성하는 것이며, 실제로 반영하지는 않는다.

```
alembic revision -m "message"
```

자동으로 새로운 버전 생성

- 버전만 생성하는 것이며, 실제로 반영하지는 않는다.

```
  alembic revision --autogenerate -m "message"
```

가장 최근 버전으로 DB 마이그레이션(upgrade) 진행

- 적용된 버전부터 현재 버전까지 변경사항을 마이그레이션을 진행해주는 기능이다.

```
  alembic upgrade head
  ```

가장 과거 버전으로 DB 마이그레이션(downgrade) 진행

```
alembic downgrade base
```

특정 버전으로 마이그레이션

```
alembic upgrade/downgrade {revisionID}
```

히스토리 확인

```
alembic history
```

## 새로운 고객사 연동 시나리오

- alembic revision head를 사용한다. 환경변수를 통해서 새로운 고객사의 mall_id를 환경 변수로 설정해서 마이그레이션 하려는 데이터베이스를 특정할 수 있다.
- 여기서 환경 변수로 설정하는 mall_id는 `common.clients` 테이블에 정의된 mall_id와 동일해야 한다.

```
TARGET_DB_NAME={mall_id} alembic upgrade head
```
