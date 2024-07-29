def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        if lookup_key in json_input:
            yield json_input[lookup_key]
        else:
            for v in json_input.values():
                yield from item_generator(v, lookup_key)

    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)


def get_data_value(data, data_name):
    """
    {
    data: 'campaign_themes': [
                                {'campaign_theme_id': 203,
                                'theme_audience_set': [
                                                        {'theme_audience_map_id': 350,
                                                        'audience_id': 'aud-000066',
                                                        'theme_cond_list': [
                                                                        {'strategy_cond_list_id': 570, 'offer_id': '202311141039-E1', 'purpose_id': 2}
                                                                        ]
                                                        },
                                                        {'theme_audience_map_id': None,
                                                        'audience_id': 'aud-000092',
                                                        'theme_cond_list': [
                                                                        {'strategy_cond_list_id': None, 'offer_id': '202311141101-E2', 'purpose_id': 4}
                                                                        ]
                                                        }
                                                    ]
                                }
                            ]
            }
    data_name: "campaign_theme_id"
    """
    return [value for value in item_generator(data, data_name) if value is not None]
