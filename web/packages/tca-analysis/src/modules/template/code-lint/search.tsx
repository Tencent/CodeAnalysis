// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect } from 'react';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Input, Form, Button } from 'coding-oa-uikit';

import SelectBorderless from '@src/components/select-borderless';
import Filter from '@src/components/filter';

const numberParams = ['checkrule_category', 'severity', 'checktool'];
const arrayParams = ['checkrule_language'];

interface SearchProps {
  filters: any;
  searchParams: any;
  loading: boolean;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const [form] = Form.useForm();
  const { searchParams, loading, filters, callback } = props;
  const {
    checkrule_category: category = [],
    checkrule_language: language = [],
    severity = [],
    checktool = [],
  } = filters as any;

  const initialValues = cloneDeep(searchParams);

  Object.entries(initialValues).forEach(([key, value]: [string, string]) => {
    if (numberParams.includes(key) && isString(value)) {
      initialValues[key] = value
        .split(',')
        .map((item: string) => toNumber(item));
    }

    if (arrayParams.includes(key) && isString(value)) {
      initialValues[key] = value.split(',');
    }
  });

  useEffect(() => {
    !loading && form.resetFields();
  }, [loading]);

  const getData = (data: any) => data.map((item: any) => ({
    value: item.value,
    text: `${item.display_name}(${item.count})`,
  }));

  const onChange = (key: string, value: any) => {
    callback({
      ...searchParams,
      [key]: value,
    });
  };

  const onClear = () => {
    form.resetFields();
    callback({});
  };

  return (
    <Filter
      form={form}
      style={{ margin: '12px 0' }}
      initialValues={initialValues}
    >
      <Filter.Item label="严重级别" name="severity">
        <SelectBorderless
          multiple
          allowClear
          placeholder="全部"
          data={getData(severity)}
          onChange={(value: any) => value && onChange('severity', value.join(','))
          }
        />
      </Filter.Item>
      <Filter.Item label="规则分类" name="checkrule_category">
        <SelectBorderless
          multiple
          allowClear
          placeholder="全部"
          data={getData(category)}
          onChange={(value: any) => value && onChange('checkrule_category', value.join(','))
          }
        />
      </Filter.Item>
      <Filter.Item label="所属工具" name="checktool">
        <SelectBorderless
          multiple
          allowClear
          placeholder="全部"
          data={getData(checktool)}
          onChange={(value: any) => value && onChange('checktool', value.join(','))
          }
        />
      </Filter.Item>
      <Filter.Item label="适用语言" name="checkrule_language">
        <SelectBorderless
          multiple
          allowClear
          placeholder="全部"
          data={getData(language)}
          onChange={(value: any) => value && onChange('checkrule_language', value.join(','))
          }
        />
      </Filter.Item>
      <Filter.Item label="" name="checkrule_name">
        <Input.Search
          size="middle"
          placeholder="规则名称"
          onSearch={value => onChange('checkrule_name', value)}
        />
      </Filter.Item>
      {Object.keys(searchParams).some((key: string) => (isArray(searchParams[key])
        ? !isEmpty(searchParams[key])
        : searchParams[key])) && (
        <Button type="link" onClick={onClear} style={{ height: '36px' }}>
          清空过滤
        </Button>
      )}
    </Filter>
  );
};

export default Search;
