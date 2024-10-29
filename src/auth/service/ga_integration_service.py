from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from src.auth.domain.ga_integration import GAIntegration
from src.auth.enums.gtm_variable import GoogleTagManagerVariableFileName
from src.auth.infra.ga_repository import GARepository
from src.auth.routes.port.base_ga_service import BaseGAIntegrationService
from src.common.utils.file.s3_service import S3Service
from src.core.exceptions.exceptions import GoogleTagException
from src.users.domain.user import User


class GAIntegrationService(BaseGAIntegrationService):

    def __init__(self, ga_repository: GARepository):
        self.scopes = [
            "https://www.googleapis.com/auth/analytics",
            "https://www.googleapis.com/auth/tagmanager",
            "https://www.googleapis.com/auth/tagmanager.edit.containers",
            "https://www.googleapis.com/auth/tagmanager.readonly",
            "https://www.googleapis.com/auth/tagmanager.publish",
            "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
        ]
        self.KEY_FILE_LOCATION = "/Users/wally/Documents/key/deeptune-1e645741bf74.json"
        self.credentials = service_account.Credentials.from_service_account_file(
            self.KEY_FILE_LOCATION, scopes=self.scopes
        )

        self.ga_repository = ga_repository
        self.s3_service = S3Service("aace-ga-script")

    async def execute_ga_automation(self, mall_id: str, user: User, db: Session) -> GAIntegration:
        mall_url = "https://cafe24.aivelabs.com"
        ga_integration = self.create_ga_settings(mall_id, mall_url, db)
        ga_integration_with_gtm = await self.create_gtm_settings(ga_integration, mall_url, db)

        return ga_integration_with_gtm

    async def create_gtm_settings(
        self, ga_integration: GAIntegration, mall_url: str, db: Session
    ) -> GAIntegration:
        tagmanager = build("tagmanager", "v2", credentials=self.credentials)
        gtm_account_id = ga_integration.gtm_account_id

        # 컨테이너 생성
        ga_integration = self.create_gtm_container(
            ga_integration, gtm_account_id, mall_url, tagmanager
        )

        # 워크스페이스 조회
        workspace_id = self.get_workspace_id(gtm_account_id, ga_integration, tagmanager)
        workspace_path = f"accounts/{gtm_account_id}/containers/{ga_integration.gtm_container_id}/workspaces/{workspace_id}"

        # 변수 생성
        await self.create_gtm_variables(tagmanager, workspace_path)

        # 트리거 생성
        # 1. DOM 사용 가능 트리거 및 태그 생성
        await self.create_dom_use_trigger_and_tag(tagmanager, workspace_path)

        # 2. 맞춤 이벤트 트리거
        self.create_custom_event_trigger_and_tag(tagmanager, workspace_path, ga_integration)

        # 모든 태그 생성(맞춤 HTML 태그, 이벤트 태그)

        # GTM 버전 생성 코드 (변경된 내용을 반영한 새로운 버전 생성)
        version_id = self.create_new_tag_version(ga_integration, tagmanager, workspace_path)

        # 버전 게시
        self.publish_new_version(ga_integration, gtm_account_id, tagmanager, version_id)

        return ga_integration

    async def create_gtm_variables(self, tagmanager, workspace_path):
        for file in GoogleTagManagerVariableFileName:
            file_key = f"gtm-variable/variable_{file.value}.js"
            response = await self.s3_service.get_object_async(file_key)
            js_content = await response["Body"].read()
            js_content = js_content.decode("utf-8")

            print(file.value)
            print(js_content)

            # 맞춤 자바스크립트 변수 생성
            variable_body = {
                "name": file.value,
                "type": "jsm",
                "parameter": [{"type": "template", "key": "javascript", "value": js_content}],
            }

            # 변수 생성 요청
            response = (
                tagmanager.accounts()
                .containers()
                .workspaces()
                .variables()
                .create(parent=workspace_path, body=variable_body)
                .execute()
            )

            print(f"{file.value} variable created: {response}")

    def publish_new_version(self, ga_integration, gtm_account_id, tagmanager, version_id):
        try:
            # 생성된 버전 ID를 사용하여 게시
            version_path = f"accounts/{gtm_account_id}/containers/{ga_integration.gtm_container_id}/versions/{version_id}"
            publish_response = (
                tagmanager.accounts().containers().versions().publish(path=version_path).execute()
            )

            print("Version published:", publish_response)

        except Exception as e:
            print("Error publishing version:", e)

    def create_new_tag_version(self, ga_integration, tagmanager, workspace_path) -> str:
        version_body = {
            "name": f"{ga_integration.mall_id}_workspace_id",
            "notes": f"{ga_integration.mall_id} 버전 생성",
        }
        try:
            version_response = (
                tagmanager.accounts()
                .containers()
                .workspaces()
                .create_version(path=workspace_path, body=version_body)
                .execute()
            )
            print("New Version created")
            print(version_response["containerVersion"]["containerVersionId"])

            return version_response["containerVersion"]["containerVersionId"]
        except Exception as e:
            print("Error creating version:", e)

    def create_custom_event_trigger_and_tag(
        self, tagmanager, workspace_path, ga_integration: GAIntegration
    ):
        custom_triggers = [
            (
                "begin_checkout_event_trigger",
                "begin_checkout",
                [("items", "{{begin_check}}"), ("value", "{{begin_check_value}}")],
            ),
            (
                "purchase_event_trigger",
                "purchase",
                [
                    ("transaction_id", "{{purchase_transaction_id}}"),
                    ("shipping", "{{purchase_shipping}}"),
                    ("value", "{{purchase_value}}"),
                    ("items", "{{purchase_items}}"),
                ],
            ),
            ("view_item_event_trigger", "view_item", [("items", "{{view_items}}")]),
        ]
        for trigger_name, event_name, event_parameter in custom_triggers:
            trigger_body = {
                "name": trigger_name,
                "type": "customEvent",  # 맞춤 이벤트 트리거 유형
                "customEventFilter": [
                    {  # customEventFilter 추가
                        "type": "equals",
                        "parameter": [
                            {
                                "type": "template",
                                "key": "arg0",
                                "value": "{{_event}}",  # Event 변수
                            },
                            {
                                "type": "template",
                                "key": "arg1",
                                "value": event_name,  # 화면에서 입력하는 이벤트 이름
                            },
                        ],
                    }
                ],
            }

            # 트리거 생성
            trigger_response = (
                tagmanager.accounts()
                .containers()
                .workspaces()
                .triggers()
                .create(parent=workspace_path, body=trigger_body)
                .execute()
            )
            trigger_id = trigger_response["triggerId"]

            tag_body = {
                "name": f"{event_name}_tag",
                "type": "gaawe",  # GA4 이벤트 태그 유형
                "parameter": [
                    {
                        "type": "template",
                        "key": "eventName",
                        "value": event_name,  # 전송할 GA4 이벤트 이름
                    },
                    {
                        "type": "list",  # 이벤트 매개변수를 위한 리스트
                        "key": "eventParameters",
                        "list": [
                            {
                                "type": "map",  # 매개변수는 맵 형식으로 전달
                                "map": [
                                    {
                                        "type": "template",
                                        "key": "name",
                                        "value": x[0],  # 이벤트 매개변수 이름
                                    },
                                    {
                                        "type": "template",
                                        "key": "value",
                                        "value": x[1],  # 데이터 레이어 변수를 참조
                                    },
                                ],
                            }
                            for x in event_parameter
                        ],
                    },
                    {
                        "type": "template",  # Measurement ID 설정
                        "key": "measurementIdOverride",
                        "value": ga_integration.ga_measurement_id,  # 여기에 실제 GA4 측정 ID 입력 (예: G-XXXXXXX)
                    },
                    {
                        "type": "boolean",  # 전자상거래 데이터 전송 활성화
                        "key": "sendEcommerceData",
                        "value": "true",
                    },
                    {
                        "type": "template",  # 데이터 소스를 Data Layer로 설정
                        "key": "ecommerceMacroDataSource",
                        "value": "dataLayer",
                    },
                ],
                "firingTriggerId": [trigger_id],  # 트리거 ID (예: DOM Ready 트리거 ID)
            }

    async def create_dom_use_trigger_and_tag(self, tagmanager, workspace_path):
        dom_use_triggers = [
            ("begin_checkout_trigger", "/order/orderform.html", "begin_checkout_push"),
            ("purchase_trigger", "/order/order_result.html", "purchase_push"),
            ("view_item_trigger", "/product/", "view_item_push"),
        ]
        for trigger_name, page_url_filter, tag_name in dom_use_triggers:
            trigger_body = {
                "name": trigger_name,
                "type": "domReady",  # DOM이 준비되었을 때 실행되는 트리거 ex (스크롤깊이: scrollDepth, 맞춤 이벤트: customEvent)
                "filter": [
                    {
                        "type": "contains",
                        "parameter": [
                            {
                                "type": "template",
                                "key": "arg0",
                                "value": "{{Page URL}}",  # Page URL 변수
                            },
                            {"type": "template", "key": "arg1", "value": page_url_filter},
                        ],
                    }
                ],
            }

            # 트리거 생성
            trigger_response = (
                tagmanager.accounts()
                .containers()
                .workspaces()
                .triggers()
                .create(parent=workspace_path, body=trigger_body)
                .execute()
            )

            trigger_id = trigger_response["triggerId"]

            file_key = f"gtm-tag/tag_{tag_name}.html"
            response = await self.s3_service.get_object_async(file_key)
            js_content = await response["Body"].read()
            js_content = js_content.decode("utf-8")

            print(tag_name)
            print(js_content)

            # 맞춤 HTML 태그 생성
            tag_body = {
                "name": tag_name,
                "type": "html",  # 태그 유형: 맞춤 HTML
                "parameter": [
                    {
                        "type": "template",
                        "key": "html",
                        "value": js_content,  # 여기에 삽입할 HTML/JS 코드
                    }
                ],
                "firingTriggerId": [trigger_id],
            }

            # 태그 생성 요청
            try:
                response = (
                    tagmanager.accounts()
                    .containers()
                    .workspaces()
                    .tags()
                    .create(parent=workspace_path, body=tag_body)
                    .execute()
                )
                print("Custom HTML Tag created:", response)

            except Exception as e:
                print("Error creating tag:", e)

    def get_workspace_id(self, gtm_account_id, gtm_container, tagmanager):
        workspaces = (
            tagmanager.accounts()
            .containers()
            .workspaces()
            .list(parent=f"accounts/{gtm_account_id}/containers/{gtm_container.gtm_container_id}")
            .execute()
        )
        workspaces_ids = [x["workspaceId"] for x in workspaces["workspace"]]
        workspace_id = max(workspaces_ids)
        return workspace_id

    def create_gtm_container(
        self, ga_integration, gtm_account_id, mall_url, tagmanager
    ) -> GAIntegration:
        container_body = {
            "name": f"{ga_integration.mall_id}_container",  # 컨테이너 이름
            "usageContext": ["web"],  # 사용 환경 (웹, Android, iOS 중 선택 가능)
            "domainName": [mall_url],  # 컨테이너가 적용될 웹사이트 도메인
        }
        try:
            new_container = (
                tagmanager.accounts()
                .containers()
                .create(parent=f"accounts/{gtm_account_id}", body=container_body)
                .execute()
            )
            print(f"Container created with ID: {new_container['containerId']}")

            ga_integration.set_gtm_container(
                new_container["containerId"], new_container["name"], new_container["publicId"]
            )

            return ga_integration
        except Exception as e:
            raise GoogleTagException(
                detail={"message": "구글 태그 매니저 변수 생성 중 오류가 발생했습니다.", "error": e}
            )

    def create_ga_settings(self, mall_id: str, mall_url: str, db: Session) -> GAIntegration:
        analytic_admin = self.create_ga_admin()

        ga_integration = self.ga_repository.get_by_mall_id(mall_id, db)

        # GA 계정 조회
        # GA 속성 생성 요청
        ga_integration = self.create_ga_property(
            ga_integration, f"{mall_id}_stream", analytic_admin
        )

        # dataStream 생성
        data_stream_type = "WEB_DATA_STREAM"
        self.create_datastream_with_enhanced_tag(
            ga_integration, mall_url, data_stream_type, analytic_admin
        )

        # ga 스크립트 확인하기
        self.get_ga_script(ga_integration, analytic_admin)

        return ga_integration

    def get_ga_script(self, ga_integration: GAIntegration, analytic_admin):
        tag_url = f"properties/{ga_integration.ga_property_id}/dataStreams/{ga_integration.ga_data_stream_id}/globalSiteTag"
        request = analytic_admin.properties().dataStreams().getGlobalSiteTag(name=tag_url)
        response = request.execute()
        return response["snippet"]

    def create_datastream_with_enhanced_tag(
        self, ga_integration: GAIntegration, mall_url, data_stream_type, analytics_admin
    ):
        data_stream_response = self.create_data_stream(
            ga_integration, analytics_admin, data_stream_type, mall_url
        )

        data_stream_parent = f"properties/{ga_integration.ga_property_id}"
        self.add_enhanced_measurement(analytics_admin, data_stream_parent)

        ga_integration = ga_integration.set_ga_data_stream(
            data_stream_response["webStreamData"]["measurementId"],
            data_stream_response["name"].split("/")[-1],
            data_stream_response["displayName"],
            mall_url,
            data_stream_type,
        )

        return ga_integration

    def create_data_stream(
        self, ga_integration: GAIntegration, analytics_admin, datastream_type, mall_url
    ):
        data_stream_body = {
            "displayName": f"{ga_integration.mall_id}_datastream",
            "webStreamData": {"defaultUri": mall_url},
            "type": datastream_type,
        }
        data_stream_parent = f"properties/{ga_integration.ga_property_id}"
        request = (
            analytics_admin.properties()
            .dataStreams()
            .create(
                parent=data_stream_parent,  # 이 부분이 인자로 들어가야 합니다.
                body=data_stream_body,
            )
        )
        data_stream_response = request.execute()
        return data_stream_response

    def add_enhanced_measurement(self, analytics_admin, data_stream_parent):
        # 향상된 측정 세팅
        enhancement_measurement_body = {
            "fileDownloadsEnabled": True,
            "formInteractionsEnabled": True,
            "outboundClicksEnabled": True,
            "pageChangesEnabled": True,
            "scrollsEnabled": True,
            "siteSearchEnabled": True,
            "streamEnabled": True,
            "videoEngagementEnabled": True,
            "searchQueryParameter": "q,s,search,query,keyword",
        }
        request = (
            analytics_admin.properties()
            .dataStreams()
            .updateEnhancedMeasurementSettings(
                name=f"{data_stream_parent}/enhancedMeasurementSettings",
                updateMask="*",
                body=enhancement_measurement_body,
            )
        )
        response = request.execute()

    def create_ga_property(
        self, ga_integration: GAIntegration, display_name, analytic_admin
    ) -> GAIntegration:
        property_parent = f"accounts/{ga_integration.ga_account_id}"
        # GA 속성 생성
        property_body = {
            "parent": property_parent,  # 여기에서 부모 계정을 지정합니다.
            "displayName": display_name,  # 원하는 속성 이름으로 변경하세요
            "timeZone": "Asia/Seoul",
            "currencyCode": "KRW",
        }
        # 속성 생성 요청
        request = analytic_admin.properties().create(body=property_body)
        response = request.execute()
        ga_integration = ga_integration.set_ga_property(
            response["name"].split("/")[-1], response["displayName"]
        )

        return ga_integration

    def create_ga_admin(self):
        return build("analyticsadmin", "v1alpha", credentials=self.credentials)