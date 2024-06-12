from src.auth.infra.cafe24_repository import Cafe24Repository
from src.contents.domain.creatives import Creatives
from src.contents.enums.image_asset_type import ImageAssetTypeEnum
from src.contents.infra.dto.response.s3_presigned_response import S3PresignedResponse
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.port.usecase.add_creatives_usecase import AddCreativesUseCase
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository
from src.utils.date_utils import get_unix_timestamp
from src.utils.file.s3_service import S3Service


class AddCreativesService(AddCreativesUseCase):
    def __init__(
        self,
        creatives_repository: BaseCreativesRepository,
        cafe24_repository: Cafe24Repository,
    ):
        self.creatives_repository = creatives_repository
        self.cafe24_repository = cafe24_repository

        # todo dot env service
        self.s3_service = S3Service("aice-asset-dev")

    def generate_s3_url(
        self, asset_data: CreativeCreate, user
    ) -> list[S3PresignedResponse]:
        cafe24_info = self.cafe24_repository.get_cafe24_info_by_user_id(
            str(user.user_id)
        )
        files = asset_data.files

        if asset_data.image_asset_type.value == ImageAssetTypeEnum.STYLE_IMAGE.value:
            prefix = asset_data.style_cd
        else:
            prefix = ImageAssetTypeEnum.NON_STYLE_IMAGE.value

        if prefix is None:
            raise Exception()

        s3_presigned_url_list = [
            S3PresignedResponse(
                original_file_name=file_name,
                s3_presigned_url=self.s3_service.generate_presigned_url_for_put(
                    f"{cafe24_info.mall_id}/image_asset/{prefix}/{get_unix_timestamp()}_{file_name}"
                ),
            )
            for file_name in files
        ]

        return s3_presigned_url_list

    def create_creatives(self, asset_data: CreativeCreate, user) -> list[Creatives]:
        files = asset_data.files

        new_creatives_list = [
            Creatives(
                image_uri=file_name,
                image_path=file_name,
                image_asset_type=asset_data.image_asset_type.value,
                style_cd=asset_data.style_cd,
                style_object_name=asset_data.style_object_name,
                creative_tags=asset_data.creative_tags,
                created_by=str(user.user_id),
                updated_by=str(user.user_id),
            )
            for file_name in files
        ]

        self.creatives_repository.create_creatives(new_creatives_list)

        return new_creatives_list


# async def save_image_asset(
#     file,
#     prefix="",
#     resource_path="app/resources/image_asset",
#     custom_name=None,
# ) -> tuple[str, str]:
#     """이미지 에셋을 업로드하는 함수
#
#     Args:
#         file: 업로드된 파일 오브젝트
#         resource_path: 저장될 경로
#     """
#     img_dir = pathlib.Path.cwd() / resource_path
#
#     # 저장될 파일 이름 생성하기
#     if custom_name:
#         image_name = custom_name
#     image_name = str(pathlib.Path(prefix) / pathlib.Path(file.filename))
#     image_path = img_dir / image_name
#     ext = image_name.split(".")[-1]
#
#     # pathlib으로 파일 존재 여부 확인(image_path)
#     if image_path.exists():
#         # 파일이 존재하면 파일 이름 변경
#         name_list = image_name.split(".")
#         name_part, extension = name_list[0], name_list[1]
#         image_name = f"{name_part}_{int(time.time())}.{extension}"
#         image_path = img_dir / image_name
#
#     # 파일 저장
#     try:
#         data = await file.read()
#         image_data = io.BytesIO(data)
#         with Image.open(image_data) as img:
#             resize_cnts = image_resize(img, extension=ext, width=600)
#         # aiofiles를 사용해 비동기적으로 파일에 쓰기
#         async with aiofiles.open(image_path, "wb") as f:
#             await f.write(resize_cnts)  # type: ignore
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "image_asset/upload",
#                 "message": f"이미지 저장에 실패하였습니다.({e})",
#             },
#         ) from e
#     finally:
#         await file.close()
#
#     return str(image_name), str(image_path)
#
#
# async def delete_image_asset(image_name, resource_path="app/resources/image_asset"):
#     """이미지 에셋을 삭제하는 함수
#
#     Args:
#         image_name: 삭제할 이미지 이름
#         resource_path: 저장될 경로
#     """
#     image_path = pathlib.Path.cwd() / resource_path / image_name
#
#     # pathlib으로 파일 존재 여부 확인(image_path)
#     if image_path.exists():
#         # 파일이 존재하면 파일 삭제
#         try:
#             os.remove(image_path)
#         except Exception as err:
#             raise HTTPException(
#                 status_code=500,
#                 detail={
#                     "code": "image_asset/delete",
#                     "message": "이미지 삭제에 실패하였습니다.",
#                 },
#             ) from err
#
#     return True


# def image_resize(img, extension, width=600, file_size: int = None):
#     """이미지 리사이즈 함수
#
#     Args:
#         img: 이미지 파일
#         extension: 이미지 확장자(jpg, jpeg, png만 지원)
#         width: 리사이즈할 기준 너비
#         file_size: 파일 사이즈 제한(optional, kb 단위)
#     """
#     # extension Check
#     extension = extension.lower()
#     if extension in ("jpg", "jpeg"):
#         extension = "JPEG"
#     elif extension == "png":
#         extension = "PNG"
#     else:
#         raise HTTPException(
#             status_code=500,
#             detail={
#                 "code": "image_asset/upload",
#                 "message": "지원하지 않는 이미지 확장자입니다.",
#             },
#         )
#
#     original_width, original_height = img.size
#     if original_width <= width:
#         return img
#     aspect_ratio = original_height / original_width
#
#     # 새로운 높이를 계산 (가로 길이를 600으로 고정)
#     new_height = int(width * aspect_ratio)
#
#     # 이미지 리사이즈
#     resized_img = img.resize((width, new_height), Image.LANCZOS)
#     img_byte_arr = io.BytesIO()
#     resized_img.save(img_byte_arr, format=extension)
#     img_byte_arr = img_byte_arr.getvalue()
#
#     ## 이미지의 파일 사이즈 제한이 필요한 경우 퀄리티로 조절
#     if file_size:
#         file_size = file_size * 1024  # kb to byte
#         quality = 95
#         while len(img_byte_arr) > file_size:
#             resized_img = resized_img.resize((width, new_height), Image.LANCZOS)
#             img_byte_arr = io.BytesIO()
#             resized_img.save(img_byte_arr, format=extension, quality=quality)
#             img_byte_arr = img_byte_arr.getvalue()
#             quality -= 5
#
#     return img_byte_arr
