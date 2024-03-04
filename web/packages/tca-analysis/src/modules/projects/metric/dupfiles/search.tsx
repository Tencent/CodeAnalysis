// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect } from 'react';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Input, Form, Button } from 'coding-oa-uikit';

import SelectBorderless from '@src/components/select-borderless';
import Filter from '@src/components/filter';

import { DUP_FILE_STATE_OPTIONS } from '../../constants';

import commonStyle from '../style.scss';

const numberParams = ['issue_state'];

interface SearchProps {
  searchParams: any;
  loading: boolean;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const [form] = Form.useForm();
  const { searchParams, loading, callback } = props;

  const initialValues = cloneDeep(searchParams);

  useEffect(() => {
    if (!loading) {
      // 表单数据格式化
      Object.entries(initialValues).forEach(([key, value]: [string, string]) => {
        if (numberParams.includes(key) && isString(value)) {
          initialValues[key] = value.split(',').map((item: string) => toNumber(item));
        }
      });

      form.resetFields();
    }
  }, [loading]);

  const onChange = (key: string, value: any) => {
    callback({
      ...searchParams,
      [key]: value,
    });
  };

  const onClear = () => {
    form.resetFields();
    callback({ ordering: searchParams.ordering });
  };

  return (
    <div className={commonStyle.ccSearchHeader}>
      <div className={commonStyle.fileHeader}>
        <Filter
          form={form}
          initialValues={initialValues}
        >
          <Filter.Item label='状态' name='issue_state' >
            <SelectBorderless
              allowClear
              placeholder='全部'
              data={DUP_FILE_STATE_OPTIONS}
              onChange={(value: any) => value && onChange('issue_state', value)}
            />
          </Filter.Item>
          <Filter.Item name='issue_owner' >
            <Input.Search
              size='middle'
              style={{ width: '140px' }}
              placeholder='责任人'
              onSearch={(value: string) => onChange('issue_owner', value)}
            />
          </Filter.Item>
          <Filter.Item name='file_path' >
              <Input.Search
                size='middle'
                style={{ width: '140px' }}
                placeholder='文件路径'
                onSearch={(value: string) => onChange('file_path', value)}
              />
            </Filter.Item>
            <Filter.Item name='duplicate_rate_gte' >
              <Input.Search
                size='middle'
                style={{ width: '140px' }}
                placeholder='重复率 >='
                onSearch={(value: string) => onChange('duplicate_rate_gte', value)}
              />
            </Filter.Item>
            <Filter.Item name='duplicate_rate_lte' >
              <Input.Search
                size='middle'
                style={{ width: '140px' }}
                placeholder='重复率 <='
                onSearch={(value: string) => onChange('duplicate_rate_lte', value)}
              />
            </Filter.Item>
          {
            Object.keys(searchParams)
              .filter((key: string) => key !== 'ordering')
              .some((key: string) => (isArray(searchParams[key]) ? !isEmpty(searchParams[key]) : searchParams[key]))
            && (
              <Button type='link' onClick={onClear} className="ml-12" style={{ height: '36px' }}>清空过滤</Button>
            )
          }
        </Filter>
      </div>
    </div>
  );
};

export default Search;
