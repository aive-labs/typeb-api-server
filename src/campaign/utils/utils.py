import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def set_summary_sententce(set_cus_count, set_df):
    audience_cnt = len(set(set_df["audience_id"]))
    audience_names = ",".join(set(set_df["audience_name"]))
    avg_response_rate = round(set_df["response_rate"].mean(), 1)
    avg_audience_unit_price = round(set_df["audience_unit_price"].mean())

    sentence_1 = f"세트 고객수는 총 {set_cus_count:,} 명입니다."
    sentence_2 = f"{audience_cnt}개의 오디언스({audience_names})로 구성되었습니다."
    sentence_3 = f"해당 오디언스들의 반응률 평균치는 {avg_response_rate}% 입니다."
    sentence_4 = f"해당 오디언스들의 객단가 평균값은 {avg_audience_unit_price:,}원 입니다."

    recipient_descriptions = [sentence_1, sentence_2, sentence_3, sentence_4]

    return recipient_descriptions


def split_dataframe_by_ratios(df, ratio_tuple: list):
    splits = []
    total_size = len(df)
    remaining_size = total_size

    for i, (group_sort_num, ratio) in enumerate(ratio_tuple):
        # 분할할 데이터의 크기 (마지막 비율이라면 남은 모든 데이터 할당)
        split_size = int(round(ratio * total_size)) if int(round(ratio * total_size)) > 0 else 1
        # 분할 # replace=False 뽑힌 데이터는 다시 뽑히지 않음
        if i < len(ratio_tuple) - 1:
            split_indices = np.random.choice(df.index, split_size, replace=False)
            split_df = df.loc[split_indices].copy()
            df = df.drop(split_indices)
        else:
            split_df = df

        split_df["group_sort_num"] = f"{group_sort_num}"
        # 결과에 추가
        splits.append(split_df)
        remaining_size -= split_size

    # 모든 분할을 합친 후 반환
    return pd.concat(splits)


def split_df_stratified_by_column(df, initial_ratios: list, stratify_column):
    """그룹 선택시 mix_lv1을 유지하면서 데이터를 분할하는 함수"""
    result_df = pd.DataFrame()
    remaining_df = df.copy()
    if not pd.api.types.is_categorical_dtype(remaining_df[stratify_column]):
        remaining_df[stratify_column] = remaining_df[stratify_column].astype("category")

    total_remaining_ratio = sum([item[1] for item in initial_ratios])

    for i, (group_sort_num, ratio) in enumerate(initial_ratios):
        # 현재 비율 계산
        current_ratio = ratio / total_remaining_ratio
        ## 방어 로직 (카테고리 train_test_split 적용시 카테고리가 1개인 경우 에러 발생)
        # 테이블에서 카테고리의 원소값이 하나만 있는 경우 찾기
        group_sizes = remaining_df.groupby(stratify_column, observed=True).size()
        # 크기가 1인 그룹만 필터링
        single_item_classes = group_sizes[group_sizes == 1].index
        # 원본 데이터 프레임에서 크기가 1인 클래스에 해당하는 행만 추출
        df_single_items = remaining_df[remaining_df[stratify_column].isin(single_item_classes)]
        if len(df_single_items) > 0:
            remaining_df = remaining_df.drop(df_single_items.index)
            if not pd.api.types.is_categorical_dtype(remaining_df[stratify_column]):
                remaining_df[stratify_column] = remaining_df[stratify_column].astype("category")

        # 남은 데이터와 비율을 업데이트
        if i < len(initial_ratios) - 1:
            # train_test_split을 사용하여 stratify 적용하여 데이터 분할
            split_df, remaining_df = train_test_split(
                remaining_df,
                test_size=1.0 - current_ratio,
                stratify=remaining_df[stratify_column],
                random_state=i,
            )
            remaining_df[stratify_column] = remaining_df[
                stratify_column
            ].cat.remove_unused_categories()
        else:
            # 마지막 그룹에는 남은 모든 데이터 할당
            split_df = remaining_df

        if len(df_single_items) > 0:
            split_df = pd.concat(  # pyright: ignore [reportCallIssue]
                [split_df, df_single_items],  # pyright: ignore [reportArgumentType]
                ignore_index=True,  # pyright: ignore [reportArgumentType]
            )  # pyright: ignore [reportCallIssue]

        # 결과 데이터프레임에 분할된 데이터 추가
        split_df["group_sort_num"] = (  # pyright: ignore [reportArgumentType, reportCallIssue]
            f"{group_sort_num}"  # pyright: ignore [reportArgumentType, reportCallIssue]
        )

        result_df = pd.concat(  # pyright: ignore [reportCallIssue]
            [result_df, split_df], ignore_index=True  # pyright: ignore [reportArgumentType]
        )  # pyright: ignore [reportCallIssue]

        # 전체에서 사용된 비율 제거
        total_remaining_ratio -= ratio

    return result_df
