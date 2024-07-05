import sys
import yaml
import random
import pandas as pd
from datetime import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import chardet

class create_data_dict:
    def __init__(self) -> None:
        self.file_path = 'src/core/data/'

    def load_yaml(self):
        # YAML 파일을 읽어서 딕셔너리로 반환
        with open(self.file_path+'msg_predefine.yaml', 'rb') as f:
            raw_data = f.read()
        # 인코딩 감지
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        with open(self.file_path+'msg_predefine.yaml', encoding=encoding) as f:
            return yaml.full_load(f)

    def generate_data_dict(self, request_generate_group_seq, input_data):
        #data_dict 초기값 설정
        data_dict={
            'campaign_type':'custom',
            'audience_type':'custom',
            'is_personalized':False,
            'product_yn':'n',
            'offer_yn':'n',
            'contents_yn':'n',
            'media':'lms',
            'msg_type':'lms'
        }

        config = create_data_dict.load_yaml(self)

        data_dict['group_idx'] = request_generate_group_seq
        
        # 캠페인 테마 (세그먼트/커스텀)
        if input_data['set_data'].get('recsys_model_id') is not None and input_data['set_data'].get('recsys_model_id') in [1,2,3,4,6,8,9,10,11,12,13]:
            data_dict['campaign_type'] = 'segment'
            data_dict['recsys_model_name'] = config['recsys_mode_name'][input_data['set_data'].get('recsys_model_id')]

        # 타겟 오디언스 (세그먼트/커스텀)
        if input_data['base_data'].get('audience_type_code')=='s':
            data_dict['audience_type'] = 'segment'
            data_dict['audience_name'] = input_data['set_data']['audience_name']
            data_dict['audience_purpose'] = config['cus_purpose'][data_dict['audience_name'][1:2]]
            data_dict['audience_purchase_level'] = data_dict['audience_name'][:1]
            data_dict['audience_promotion_level'] = data_dict['audience_name'][2:]

        # 개인화 여부
        if input_data['base_data'].get('is_personalized')==True:
            data_dict['is_personalized'] = input_data['base_data']['is_personalized']

        # 캠페인 기본 정보 (캠페인명, 시작일, 완료일)
        data_dict['campaign_name'] = input_data['base_data'].get('campaign_name')
        data_dict['start_date'] = input_data['base_data'].get('start_date')
        data_dict['end_date'] = input_data['base_data'].get('end_date')
        
        # 상품 유무 체크 
        if input_data['set_data'].get('rep_nm_list') is not None and len(input_data['set_data']['rep_nm_list'])!=0:
            data_dict['product_yn'] = 'y'
        
        # 오퍼 유무 체크 
        if input_data['set_data'].get('offer_info') is not None and len(input_data['set_data']['offer_info'])!=0:
            data_dict['offer_yn'] = 'y'
            data_dict['offer_info'] = input_data['set_data']['offer_info']
        
        # 그룹별 데이터 가져오기
        group_num = 0
        for i,v in enumerate(input_data['group_info']):
            if str(v['set_group_seq']) == str(request_generate_group_seq):
                group_num = i

                # 콘텐츠 
                if input_data['group_info'][group_num].get('contents_name') is not None:
                    data_dict['contents_yn'] = 'y'
                    data_dict['contents_id'] = input_data['group_info'][group_num].get('contents_id')
                    data_dict['contents_name'] = input_data['group_info'][group_num].get('contents_name')
                    if 'contents_url' in input_data['group_info'][group_num].keys():
                        data_dict['contents_url'] = input_data['group_info'][group_num].get('contents_url')

                # 대표상품명 입력 (group_info.rep_nm)
                if 'rep_nm' in input_data['group_info'][group_num].keys() and input_data['group_info'][group_num].get('rep_nm') is not None:
                    data_dict['rep_nm'] = input_data['group_info'][group_num].get('rep_nm')
                
                # 그룹 개인화 변수 
                if 'set_group_category' in input_data['group_info'][group_num].keys() and input_data['group_info'][group_num].get('set_group_category') is not None:
                    data_dict['set_group_category'] = input_data['group_info'][group_num].get('set_group_category').value
                    data_dict['set_group_val'] = input_data['group_info'][group_num].get('set_group_val')
                    if input_data['group_info'][group_num].get('set_group_category') == 'purpose':
                        data_dict['audience_purpose'] = input_data['group_info'][group_num].get('set_group_val')
                    if data_dict['set_group_category'] == 'rep_nm' and 'rep_nm' not in data_dict.keys():
                        data_dict['rep_nm'] = data_dict['set_group_val']
                
                # 문자 표출 형식 (lms/카카오톡 등)
                if 'media' in input_data['group_info'][group_num].keys(): 
                    data_dict['media'] = input_data['group_info'][group_num]['media'].value
                if 'msg_type' in input_data['group_info'][group_num].keys(): 
                    data_dict['msg_type'] = input_data['group_info'][group_num]['msg_type'].value
                
                # 그룹 통계 변수 
                if 'group_stats' in input_data['group_info'][group_num].keys():
                    if 'item_ratio' in input_data['group_info'][group_num]['group_stats'].keys():
                        item_ratio = input_data['group_info'][group_num]['group_stats'].get('item_ratio')
                        if item_ratio is not None:
                            for k,v in item_ratio.items():
                                if v>=0.8 and k in config['item_nm'].keys():
                                    data_dict['prd_item_nm']=config['item_nm'][k]
                    if 'style_seg_ratio' in input_data['group_info'][group_num]['group_stats'].keys():
                        style_seg_ratio = input_data['group_info'][group_num]['group_stats'].get('style_seg_ratio')
                        if style_seg_ratio is not None:
                            for k,v in style_seg_ratio.items():
                                if v>=0.8:
                                    data_dict['audience_purpose']=config['style_seg'][k]
                    if 'rep_purpose_ratio' in input_data['group_info'][group_num]['group_stats'].keys():
                        rep_purpose_ratio = input_data['group_info'][group_num]['group_stats'].get('rep_purpose_ratio')
                        if rep_purpose_ratio is not None:
                            for k,v in rep_purpose_ratio.items():
                                if v>=0.8:
                                    data_dict['rep_purpose']=config['rep_purpose'][k]
                    if 'age_ratio' in input_data['group_info'][group_num]['group_stats'].keys():
                        age_ratio = input_data['group_info'][group_num]['group_stats'].get('age_ratio')
                        if age_ratio is not None:
                            young = 0
                            old = 0
                            for k,v in age_ratio.items():
                                if k in ['20대','30대']:
                                    young = young + float(v)
                                else:
                                    old = old + float(v)
                            if young >= 0.8:
                                data_dict['audience_age'] = '2030'
                            elif old >= 0.8:
                                data_dict['audience_age'] = '5060'
        return data_dict

    def create_data_dict(self, request_generate_group_seq, input_data):
        config = create_data_dict.load_yaml(self)
        data_dict = create_data_dict.generate_data_dict(self, request_generate_group_seq, input_data)

        if 'campaign_name' in data_dict.keys():
            ## 캠페인 키워드 매칭
            for k,v in config['campaign_keyword'].items():
                for keyword in v.split(','):
                    if keyword in data_dict['campaign_name'].replace(" ","").lower():
                        data_dict['campaign_keyword'] = k

            ## 시즌 매칭 - 키워드로
            for k,v in config['season_keyword'].items():
                for keyword in v.split(','):
                    if keyword in data_dict['campaign_name'].replace(" ","").lower():
                        data_dict['season'] = k
                        break

        if 'start_date' in data_dict.keys() and 'season' not in data_dict.keys():
            ## 시즌 매칭 - 날짜로
            st_year = int(data_dict['start_date'][:4])
            start_date = datetime.strptime(data_dict['start_date'],"%Y%m%d")

            season_list = []
            for k,v in config['season_date'].items():
                open_date = datetime.strptime(v[0],"%m/%d")
                close_date = datetime.strptime(v[1],"%m/%d")

                if open_date.month>close_date.month:
                    if start_date.month < open_date.month:
                        open_date = open_date.replace(year=st_year-1)
                        close_date = close_date.replace(year=st_year)
                    else:
                        open_date = open_date.replace(year=st_year)
                        close_date = close_date.replace(year=st_year+1)
                else:
                    open_date = open_date.replace(year=st_year)
                    close_date = close_date.replace(year=st_year)
                    
                if k in ['설날','추석']:
                    calendar = KoreanLunarCalendar()
                    calendar.setLunarDate(open_date.year,open_date.month,open_date.day,False)
                    open_date = calendar.SolarIsoFormat()
                    open_date = datetime.strptime(open_date,'%Y-%m-%d')
                    
                    calendar.setLunarDate(close_date.year,close_date.month,close_date.day,False)
                    close_date = calendar.SolarIsoFormat()
                    close_date = datetime.strptime(close_date,'%Y-%m-%d')
                    
                if start_date>=open_date and start_date<=close_date:
                    season_list.append(k)
                    
            data_dict['season'] = random.choice(season_list)
        
        if 'season' not in data_dict.keys():
            data_dict['season'] = '공통'
        
        if data_dict.get('campaign_keyword')=='얼리버드' and data_dict['season'] in ['봄','여름','초봄','초여름']:
            data_dict['campaign_keyword'] = 'SS시즌 얼리버드'
        elif data_dict.get('campaign_keyword')=='얼리버드' and data_dict['season'] in ['가을','겨울','초가을','초겨울']:
            data_dict['campaign_keyword'] = 'FW시즌 얼리버드'

        return data_dict


class generate_message:
    def __init__(self) -> None:
        self.file_path = 'src/core/data/'
        self.msg_data = pd.read_csv(self.file_path+'msg_data.csv',encoding='euc-kr')
        self.msg_data['age'] = self.msg_data['age'].fillna(0)
        self.msg_data['age'] = self.msg_data['age'].astype(int).astype(str)

        self.offer_df = pd.read_csv(self.file_path+'msg_offer_temp.csv')
        self.notice_df = pd.read_csv(self.file_path+'msg_notice_temp.csv')
        self.rep_tag = pd.read_csv(self.file_path+'rep_tag.csv',encoding='euc-kr')
        self.text_temp = pd.read_csv(self.file_path+'text_template.csv')
        self.extra_df = pd.read_csv(self.file_path+'rep_extra_text.csv',encoding='euc-kr')

        self.msg_gen_key = []
        self.msg_title = ''
        self.msg_body = ''
        self.rec_explanation = []
        self.msg_link_button = []

    def load_yaml(self):
        # YAML 파일을 읽어서 딕셔너리로 반환
        with open(self.file_path+'msg_predefine.yaml', 'rb') as f:
            raw_data = f.read()
        # 인코딩 감지
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        with open(self.file_path+'msg_predefine.yaml', encoding=encoding) as f:
            return yaml.full_load(f)
        
    def contents_only(self, data_dict):
        contents_df = self.text_temp[(self.text_temp['index']=='contents_only')&(self.text_temp['detail']==data_dict.get('audience_purpose'))].sample(n=1)
        contents_text = contents_df['text'].values[0]
        contents_text = contents_text.replace('\r','')
        title = contents_text[:contents_text.find('\n\n')]
        body = contents_text[contents_text.find('\n\n')+2:]
        if data_dict.get('msg_type') in ['lms','mms']:
            self.msg_title = title
            self.msg_body = body
            self.msg_gen_key.append(contents_df['gen_key'].values[0])
        elif data_dict.get('msg_type') in ['kakao_text','kakao_image_general']:
            self.msg_title = title
            self.msg_body = contents_text
            self.msg_gen_key.append(contents_df['gen_key'].values[0])
        elif data_dict.get('msg_type') in ['kakao_image_wide']:
            self.msg_body = title
            self.msg_gen_key.append(contents_df['gen_key'].values[0])

    def remind(self, data_dict):
        contents_df = self.text_temp[(self.text_temp['index']=='remind')].sample(n=1)
        contents_text = contents_df['text'].values[0]
        contents_text = contents_text.replace('\r','')
        title = contents_text[:contents_text.find('\n\n')]
        body = contents_text[contents_text.find('\n\n')+2:]
        if data_dict.get('msg_type') in ['lms','mms']:
            self.msg_title = title
            self.msg_body = body
            self.msg_gen_key.append(contents_df['gen_key'].values[0])
        elif data_dict.get('msg_type') in ['kakao_text','kakao_image_general']:
            self.msg_title = title
            self.msg_body = contents_text
            self.msg_gen_key.append(contents_df['gen_key'].values[0])
        elif data_dict.get('msg_type') in ['kakao_image_wide']:
            self.msg_body = title
            self.msg_gen_key.append(contents_df['gen_key'].values[0])

    def generate_title(self, data_dict):
        msg_title_df = self.msg_data[self.msg_data['location']=='title']

        sample_df = pd.DataFrame()
        if 'audience_purpose' in data_dict.keys():
            sample_df = pd.concat([sample_df,msg_title_df[(msg_title_df['index'].str.startswith('cs'))&(msg_title_df['detail']==data_dict['audience_purpose'])]])
        if 'recsys_model_name' in data_dict.keys():
           sample_df = pd.concat([sample_df,msg_title_df[(msg_title_df['index'].str.startswith('st'))&(msg_title_df['detail']==data_dict['recsys_model_name'])]])
        if 'campaign_keyword' in data_dict.keys():
            sample_df = pd.concat([sample_df,msg_title_df[(msg_title_df['index'].str.startswith('k_'))&(msg_title_df['detail']==data_dict['campaign_keyword'])]])
        if data_dict.get('offer_yn')=='y' and 'offer_info' in data_dict.keys():
            if 'offer_type_name' in data_dict['offer_info'].keys():
                sample_df = pd.concat([sample_df,msg_title_df[(msg_title_df['index'].str.startswith('o_'))&(msg_title_df['detail']==data_dict['offer_info']['offer_type_name'])]])

        if data_dict.get('product_yn')=='y':
            sample_df = pd.concat([sample_df,msg_title_df[(msg_title_df['index'].str.startswith('sp'))&(msg_title_df['detail']==data_dict['season'])]])
        if data_dict.get('offer_yn')=='y':
            sample_df = pd.concat([sample_df,msg_title_df[(msg_title_df['index'].str.startswith('so'))&(msg_title_df['detail']==data_dict['season'])]])
        if data_dict.get('product_yn')=='n' and data_dict.get('offer_yn')=='n':
            sample_df = pd.concat([sample_df,msg_title_df[(msg_title_df['index'].str.startswith('ss'))&(msg_title_df['detail']==data_dict['season'])]])

        basic = sample_df.sample(n=1)
        self.msg_gen_key.append(basic['gen_key'].values[0])
        self.msg_title = basic['text'].values[0]
        if data_dict['msg_type'] not in ('lms','mms') and data_dict['msg_type']!='kakao_image_wide':
            self.msg_body = basic['text'].values[0] + '\n\n'


    def generate_body(self, data_dict):
        msg_main_df = self.msg_data[self.msg_data['location']=='main']

        sample_df = pd.DataFrame()
        # 구매력 (개인화 문장) 
        if 'audience_purchase_level' in data_dict.keys() and data_dict.get('msg_type')!='kakao_image_wide':
            aud_prchs = msg_main_df[(msg_main_df['index'].str.startswith('pa'))&(msg_main_df['detail']==data_dict['audience_purchase_level'])].sample(n=1)
            self.msg_gen_key.append(aud_prchs['gen_key'].values[0])
            self.msg_body = self.msg_body + aud_prchs['text'].values[0] + '\n'
            if str(aud_prchs['rec_exp'].values[0]) != 'nan':
                self.rec_explanation.append(aud_prchs['rec_exp'].values[0])
        # 기본문장 
        if 'recsys_model_name' in data_dict.keys():
            if 'audience_age' in data_dict.keys():
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('st'))&(msg_main_df['detail']==data_dict['recsys_model_name'])&(msg_main_df['age']==data_dict.get('audience_age'))]])
            else:
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('st'))&(msg_main_df['detail']==data_dict['recsys_model_name'])]])

        if 'campaign_keyword' in data_dict.keys():
            if 'audience_age' in data_dict.keys():
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('k_'))&(msg_main_df['detail']==data_dict['campaign_keyword'])&(msg_main_df['age']==data_dict.get('audience_age'))]])
            else:
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('k_'))&(msg_main_df['detail']==data_dict['campaign_keyword'])]])

        if data_dict.get('offer_yn')=='y' and 'offer_info' in data_dict.keys():
            if 'offer_type_name' in data_dict['offer_info'].keys():
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('o_'))&(msg_main_df['detail']==data_dict['offer_info']['offer_type_name'])]])
        if data_dict.get('product_yn')=='y':
            if 'audience_age' in data_dict.keys():
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('sp'))&(msg_main_df['detail']==data_dict['season'])&(msg_main_df['age']==data_dict.get('audience_age'))]])
            else:
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('sp'))&(msg_main_df['detail']==data_dict['season'])]])
        if data_dict.get('offer_yn')=='y':
            if 'audience_age' in data_dict.keys():
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('so'))&(msg_main_df['detail']==data_dict['season'])&(msg_main_df['age']==data_dict.get('audience_age'))]])
            else:
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('so'))&(msg_main_df['detail']==data_dict['season'])]])
        if data_dict.get('product_yn')=='n' and data_dict.get('offer_yn')=='n':
            if 'audience_age' in data_dict.keys():
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('ss'))&(msg_main_df['detail']==data_dict['season'])&(msg_main_df['age']==data_dict.get('audience_age'))]])
            else:
                sample_df = pd.concat([sample_df,msg_main_df[(msg_main_df['index'].str.startswith('ss'))&(msg_main_df['detail']==data_dict['season'])]])

        basic = sample_df.sample(n=1)
        if data_dict.get('offer_yn')=='y':
            if 'offer_amount' not in data_dict['offer_info'].keys() and 'offer_amount' in basic['text'].values[0]:
                basic = sample_df.sample(n=1)
                while 'offer_amount' in basic['text'].values[0]:
                    basic = sample_df.sample(n=1)
            if 'apply_pcs' not in data_dict['offer_info'].keys() and 'apply_pcs' in basic['text'].values[0]:
                basic = sample_df.sample(n=1)
                while 'apply_pcs' in basic['text'].values[0]:
                    basic = sample_df.sample(n=1)

        self.msg_gen_key.append(basic['gen_key'].values[0])
        self.msg_body = self.msg_body + basic['text'].values[0]
        if str(basic['rec_exp'].values[0]) != 'nan':
                self.rec_explanation.append(basic['rec_exp'].values[0])

        if data_dict.get('msg_type')!='kakao_image_wide': 
            # 대표상품 전용 추가 문구 
            if data_dict.get('rep_nm')=='WHISTLIZER SHOES':
                if 'audience_purpose' in data_dict.keys() and data_dict.get('audience_purpose') is not None:
                    extra_text = self.extra_df[(self.extra_df.rep_nm==data_dict.get('rep_nm'))&(self.extra_df.detail==data_dict.get('audience_purpose'))].sample(n=1)
                else:
                    extra_text = self.extra_df[(self.extra_df.rep_nm==data_dict.get('rep_nm'))&(self.extra_df.detail=='공통')].sample(n=1)
                self.msg_gen_key.append(extra_text['gen_key'].values[0])
                self.msg_body = self.msg_body + '\n' + extra_text['text'].values[0]
                if str(extra_text['rec_exp'].values[0]) != 'nan':
                    self.rec_explanation.append(extra_text['rec_exp'].values[0])

            else:
                # 고객 SEG, 상품 PURPOSE (개인화 문장)
                try:
                    if 'audience_purpose' in data_dict.keys() and data_dict.get('msg_type')!='kakao_image_wide':
                        aud_prps = msg_main_df[(msg_main_df['index'].str.startswith('cs'))&(msg_main_df['detail']==data_dict['audience_purpose'])].sample(n=1)
                        self.msg_gen_key.append(aud_prps['gen_key'].values[0])
                        self.msg_body = self.msg_body +'\n'+ aud_prps['text'].values[0]
                        if str(aud_prps['rec_exp'].values[0]) != 'nan':
                            self.rec_explanation.append(aud_prps['rec_exp'].values[0])
                except: pass
                try:
                    if 'rep_purpose' in data_dict.keys() and data_dict.get('msg_type')!='kakao_image_wide':
                        prd_prps = msg_main_df[(msg_main_df['index'].str.startswith('pp'))&(msg_main_df['detail']==data_dict['rep_purpose'])].sample(n=1)
                        self.msg_gen_key.append(prd_prps['gen_key'].values[0])
                        self.msg_body = self.msg_body +'\n'+ prd_prps['text'].values[0]
                        if str(prd_prps['rec_exp'].values[0]) != 'nan':
                            self.rec_explanation.append(prd_prps['rec_exp'].values[0])
                except: pass

            # 대표상품명에 따라 해쉬태그 표출 (랜덤 3개)
            try:
                if 'rep_nm' in data_dict.keys() and data_dict.get('msg_type')!='kakao_image_wide':
                    if data_dict.get('rep_nm') in self.rep_tag['rep_nm'].values:
                        rep_tags = (self.rep_tag[self.rep_tag['rep_nm']==data_dict.get('rep_nm')]['tag'].values[0]).split(' ')
                        if len(rep_tags) >= 3:
                            rep_tags = ' '.join(random.sample(rep_tags,3))
                        else:
                            rep_tags = ' '.join(rep_tags)
                        self.msg_body = self.msg_body + '\n' + rep_tags
            except: pass

    def product_template(self, data_dict):
        """
        {{추천상품명}} 부분은 개인화변수 (개인별로 적용 값이 다름)
        """
        if 'rep_nm' in data_dict.keys():
            self.msg_body = self.msg_body + '\n\n▷ 추천 상품: '+data_dict['rep_nm']
        else:
            self.msg_body = self.msg_body + '\n\n▷ 추천 상품:{rep_nm}'


    def offer_template(self, data_dict):
        if data_dict['offer_info'].get('offer_amount') is None:
            data_dict['offer_info']['offer_amount'] = data_dict['offer_info'].get('offer_rate')

        ## 할인 혜택 및 강도 (of-text)
        if 'offer_amount' in data_dict['offer_info'].keys() and data_dict['offer_info'].get('offer_amount') is not None:
            offer_condition = data_dict['offer_info'].get('offer_type_name').lower()
            if data_dict['msg_type'] in ('lms','mms'):
                self.msg_body = self.msg_body + '\n\n' + self.offer_df[(self.offer_df.index_id=='of-text')&(self.offer_df.condition==offer_condition)]['text'].values[0].replace('{offer_amount}',str(format(data_dict['offer_info']['offer_amount'],',d')))
            else:
                self.msg_body = self.msg_body + '\n\n' + self.offer_df[(self.offer_df.index_id=='of-text')&(self.offer_df.condition==offer_condition)]['text'].values[0].replace('{offer_amount}',str(format(data_dict['offer_info']['offer_amount'],',d')))
        
        ## 기간
        if data_dict['msg_type']!='kakao_image_wide':
            self.msg_body = self.msg_body + '\n' + self.offer_df[(self.offer_df.index_id=='of-drt')]['text'].values[0].replace('{event_str_dt}','{offer_start_date}').replace('{event_end_dt}','{offer_end_date}')
        
    def cmp_date(self, data_dict):
        self.msg_body = self.msg_body + '\n\n▷ 기간 : {campaign_start_date}~{campaign_end_date}'

    def contents_template(self, data_dict):
        config = create_data_dict.load_yaml(self)

        if data_dict['contents_yn']=='y':
            if 'contents_url' in data_dict.keys() and data_dict.get('contents_url') is not None:
                if data_dict['msg_type'] in ('lms','mms') :
                    self.msg_body = self.msg_body + '\n\n' + '▷' + data_dict['contents_name'] + '\n' + data_dict['contents_url']
                else:
                    self.msg_link_button.append({'button_type':'web_link_button','web_link':data_dict['contents_url'],'button_name':random.choice(config['button_msg']),'app_link':data_dict['contents_url'],'set_group_msg_seq':data_dict['group_idx']})
            else:
                if data_dict['msg_type'] in ('lms','mms'):
                    self.msg_body = self.msg_body + '\n\n' + '▷ {contents_name}' + '\n' + '{contents_url}'
                else:
                    self.msg_link_button.append({'button_type':'web_link_button','web_link':'{{contents_url}}','button_name':random.choice(config['button_msg']),'app_link':'{{contents_url}}','set_group_msg_seq':data_dict['group_idx']})


    def notice_template(self, data_dict):
        self.msg_body = self.msg_body + '\n'

        ## 적용/미적용 상품
        if data_dict['msg_type']!='kakao_image_wide':
            if data_dict['offer_info'].get('offer_style_conditions')=='전 상품' and data_dict['offer_info'].get('offer_style_exclusion_conditions') is None:
                self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-style-1'].sample(n=1)['text'].values[0]
            elif data_dict['offer_info'].get('offer_style_conditions')=='전 상품' and data_dict['offer_info'].get('offer_style_exclusion_conditions') is None:
                self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-style-2'].sample(n=1)['text'].values[0]
            else:
                self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-style-3'].sample(n=1)['text'].values[0]

        ## 적용/미적용 채널
        if data_dict['msg_type']!='kakao_image_wide':
            if data_dict['offer_info'].get('offer_channel_conditions') is not None and data_dict['offer_info'].get('offer_channel_exclusion_conditions') is None:
                self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-ch-1'].sample(n=1)['text'].values[0]
            elif data_dict['offer_info'].get('offer_channel_conditions') is None and data_dict['offer_info'].get('offer_channel_exclusion_conditions') is not None:
                    self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-ch-2'].sample(n=1)['text'].values[0]
            elif data_dict['offer_info'].get('offer_channel_conditions') is not None and data_dict['offer_info'].get('offer_channel_exclusion_conditions') is not None:
                    self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-ch-3'].sample(n=1)['text'].values[0]
            elif data_dict['offer_info'].get('offer_channel_conditions') is None and data_dict['offer_info'].get('offer_channel_exclusion_conditions') is None:
                    self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-ch-4'].sample(n=1)['text'].values[0]

        ## 선택사항 (lms 형태에만 표출됨)
        if 'apply_pcs' in data_dict['offer_info'].keys():
            apply_pcs = data_dict['offer_info'].get('apply_pcs') if data_dict['offer_info'].get('apply_pcs') is not None else 1
            if apply_pcs > 1 and data_dict['media']=='lms':
                self.msg_body = self.msg_body + '\n' + self.offer_df[self.offer_df.index_id=='of-pcs']['text'].values[0].replace('[apply_pcs]',str(data_dict['offer_info']['apply_pcs']))

        if data_dict['offer_info'].get('offer_type_name') is not None:
            self.msg_body = self.msg_body + '\n' + self.notice_df[self.notice_df.condition==data_dict['offer_info']['offer_type_name']]['text'].values[0]
        else:
            self.msg_body = self.msg_body + '\n' + self.notice_df[self.notice_df.condition=='기타']['text'].values[0]
        
        

def match_real_data(data_dict, msg_title, msg_body):
    msg_title = msg_title.replace('{year}',data_dict['start_date'][:4])
    if data_dict['offer_yn']=='y':
        if data_dict['offer_info'].get('offer_amount') is not None:
            msg_title = msg_title.replace('{offer_amount}',str(format(data_dict['offer_info']['offer_amount'],',d')))
        if data_dict['offer_info'].get('apply_pcs') is not None: 
            msg_title = msg_title.replace('{apply_pcs}',str(data_dict['offer_info']['apply_pcs']))
    if 'rep_nm' in data_dict.keys() and data_dict.get('rep_nm') is not None:
        msg_title = msg_title.replace('{rep_nm}',data_dict['rep_nm'])
    
    msg_body = msg_body.replace('{year}',data_dict['start_date'][:4])
    if 'rep_nm' in data_dict.keys():
        msg_body = msg_body.replace('{rep_nm}',data_dict['rep_nm'])
    if 'set_group_category' in data_dict.keys():
        if data_dict.get('set_group_category')=='rep_nm':
            msg_body = msg_body.replace('{rep_nm}',data_dict['set_group_val'])
    if data_dict['offer_yn']=='y':
        if data_dict['offer_info'].get('offer_amount') is not None:
            msg_body = msg_body.replace('{offer_amount}',str(format(data_dict['offer_info']['offer_amount'],',d')))
        if data_dict['offer_info'].get('apply_pcs') is not None: 
            msg_body = msg_body.replace('{apply_pcs}',str(data_dict['offer_info']['apply_pcs']))
            
    msg_title = msg_title.replace('{','{{').replace('}','}}')
    msg_body = msg_body.replace('{','{{').replace('}','}}')
    return msg_title, msg_body


def generate_dm(grp_idx, input_data, send_date, msg_type, remind_duration):
    """
    grp_idx[int]
    input_data[dict]
    send_date[str]
    msg_type[str] = 'remind' or 'campagin'
    remind_duration[int] #아직 미정
    """


    if msg_type=='remind':
        inst1 = create_data_dict()
        data_dict = inst1.create_data_dict(grp_idx, input_data)
        if data_dict.get('msg_type') not in ['lms','mms','kakao_text','kakao_image_general','kakao_image_wide']:
            output = {}
            output['msg_gen_key'] = ''
            output['msg_title'] = ''
            output['msg_body'] = ''
            output['rec_explanation'] = []
            output['kakao_button_link'] = {}
        else:
            inst2 = generate_message()
            inst2.remind(data_dict)

            if data_dict['offer_yn']=='y' and data_dict['msg_type'] in ('lms','mms'):
                inst2.notice_template(data_dict)

            output = {}
            output['msg_gen_key'] = inst2.msg_gen_key
            output['msg_title'] = inst2.msg_title
            output['msg_body'] = inst2.msg_body
            output['rec_explanation'] = []
            output['kakao_button_link'] = {}

    else:
        inst1 = create_data_dict()
        data_dict = inst1.create_data_dict(grp_idx, input_data)

        if data_dict.get('msg_type') not in ['lms','mms','kakao_text','kakao_image_general','kakao_image_wide']:
            output = {}
            output['msg_gen_key'] = ''
            output['msg_title'] = ''
            output['msg_body'] = ''
            output['rec_explanation'] = []
            output['kakao_button_link'] = {}
        else:
            if data_dict.get('recsys_model_name') == 'contents_only':
                inst2 = generate_message()
                inst2.contents_only(data_dict)
                inst2.contents_template(data_dict)

            else:
                inst2 = generate_message()
                inst2.generate_title(data_dict)
                inst2.generate_body(data_dict)

                msg_link_button = []
                if data_dict['product_yn']=='y' and data_dict['msg_type'] in ('lms','mms'):
                    inst2.product_template(data_dict)
                if data_dict['offer_yn']=='y':
                    inst2.offer_template(data_dict)
                else:
                    inst2.cmp_date(data_dict)
                if data_dict['contents_yn']=='y':
                    inst2.contents_template(data_dict)
                if data_dict['offer_yn']=='y' and data_dict['msg_type'] in ('lms','mms'):
                    inst2.notice_template(data_dict)

            msg_title = inst2.msg_title
            msg_body = inst2.msg_body
            rec_explanation = inst2.rec_explanation
            msg_link_button = inst2.msg_link_button

            rec_explanation = list(set((','.join(rec_explanation)).split(',')))

            msg_title, msg_body = match_real_data(data_dict, msg_title, msg_body)
            
            output = {}
            output['msg_gen_key'] = ';'.join(inst2.msg_gen_key)
            output['msg_title'] = msg_title
            output['msg_body'] = msg_body
            output['rec_explanation'] = rec_explanation
            output['kakao_button_link'] = msg_link_button

    return output