// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect } from 'react';
import { toNumber, isString, isEmpty, isArray, cloneDeep, find } from 'lodash';
import { Input, Form, Button, Select } from 'coding-oa-uikit';

import SelectBorderless from '@src/components/select-borderless';
import Filter from '@src/components/filter';
import { SEVERITY, CATEGORY } from '../constants';

const numberParams = ['checkpackage', 'severity', 'category'];
const arrayParams = ['language_name'];

interface SearchProps {
  filters: any;
  searchParams: any;
  loading: boolean;
  addToolsRules: (toolId: number) => void;  // 一键添加工具所有规则
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const [form] = Form.useForm();
  const { searchParams, loading, filters, addToolsRules, callback } = props;
  const { allPkgs = [], languages = [], checkTools = [] }: any = filters;

  const initialValues = cloneDeep(searchParams);

  Object.entries(initialValues).forEach(([key, value]: [string, string]) => {
    if (numberParams.includes(key) && isString(value)) {
      initialValues[key] = value
        .split(',')
        .map((item: string) => toNumber(item));
    }

    if (initialValues.checktool) {
      initialValues.checktool = toNumber(initialValues.checktool);
    }

    if (arrayParams.includes(key) && isString(value)) {
      initialValues[key] = value.split(',');
    }
  });

  useEffect(() => {
    !loading && form.resetFields();
  }, [loading]);

  const getData = (data: any) => data.map((item: any) => ({
    value: item.id,
    text: item.name,
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
      <Filter.Item label="官方规则包" name="checkpackage">
        <SelectBorderless
          multiple
          allowClear
          placeholder="全部"
          data={getData(allPkgs)}
          onChange={(value: any) => value && onChange('checkpackage', value.join(','))
          }
        />
      </Filter.Item>
      <Filter.Item label="严重级别" name="severity">
        <SelectBorderless
          multiple
          allowClear
          placeholder="全部"
          data={Object.entries(SEVERITY).map(([key, value]: [string, string]) => ({
            value: toNumber(key),
            text: value,
          }))}
          onChange={(value: any) => value && onChange('severity', value.join(','))
          }
        />
      </Filter.Item>
      <Filter.Item label="规则分类" name="category">
        <SelectBorderless
          multiple
          allowClear
          placeholder="全部"
          data={Object.entries(CATEGORY).map(([key, value]: [string, string]) => ({
            value: toNumber(key),
            text: value,
          }))}
          onChange={(value: any) => value && onChange('category', value.join(','))
          }
        />
      </Filter.Item>
      <Filter.Item label="适用语言" name="language_name">
        <SelectBorderless
          allowClear
          placeholder="全部"
          data={languages?.map((item: any) => ({
            value: item.name,
            text: item.display_name,
          }))}
          onChange={(value: any) => onChange('language_name', value)
          }
        />
      </Filter.Item>
      <Filter.Item label="所属工具" name="checktool">
        <Select
          showSearch
          allowClear
          size='middle'
          placeholder='全部工具'
          style={{ minWidth: '150px' }}
          optionFilterProp='children'
          dropdownMatchSelectWidth={false}
          onChange={(value: any) => onChange('checktool', value)}
        >
          {
            checkTools.map((item: any) => (
              <Select.Option key={item.id} value={item.id}>{item.display_name}</Select.Option>
            ))
          }
        </Select>
        {/* <SelectBorderless
          allowClear
          placeholder="全部"
          data={checkTools?.map((item: any) => ({
            value: item.id,
            text: item.display_name,
          }))}
          onChange={(value: any) => value && onChange('checktool', value.join(','))
          }
        /> */}
      </Filter.Item>
      <Filter.Item label="" name="real_name">
        <Input.Search
          size="middle"
          placeholder="规则名称"
          style={{ minWidth: '150px' }}
          onSearch={value => onChange('real_name', value)}
        />
      </Filter.Item>
      {Object.keys(searchParams).some((key: string) => (isArray(searchParams[key])
        ? !isEmpty(searchParams[key])
        : searchParams[key])) && (
          <Button type="link" onClick={onClear} style={{ height: '36px', marginRight: 10 }}>
            清空过滤
          </Button>
      )}
      {
        find(checkTools, { id: initialValues.checktool }) && (
          <Button type="link" style={{ height: '36px' }} onClick={() => addToolsRules(initialValues.checktool)}>
            一键添加 {find(checkTools, { id: initialValues.checktool })?.display_name} 工具的所有规则
          </Button>
        )
      }
    </Filter>
  );
};

export default Search;
