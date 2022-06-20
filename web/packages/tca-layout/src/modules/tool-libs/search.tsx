/**
 * 规则列表搜索栏
 */
import React, { useEffect } from 'react';
import { cloneDeep, isArray, isEmpty } from 'lodash';
import { Button, Form, Input, Select } from 'coding-oa-uikit';

import Filter from '@src/components/filter';
import { LIB_ENV } from './constants';

import style from './style.scss';

interface SearchProps {
  orgSid: string;
  loading: boolean;
  editable: boolean;
  searchParams: any;
  onAdd: () => void;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const { searchParams, loading, editable, onAdd, callback } = props;
  const [form] = Form.useForm();
  const initialValues = cloneDeep(searchParams);

  useEffect(() => {
    if (!loading) {
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
    callback({});
  };

  return (
    <div className={style.filter}>
      <Filter
        form={form}
        initialValues={{
          ...initialValues,
          os: initialValues.os?.split(',') ?? []
        }}
      >
        <Filter.Item name='name' >
          <Input.Search
            size='middle'
            style={{ width: '160px' }}
            placeholder='依赖名称'
            onSearch={(value: string) => onChange('name', value)}
          />
        </Filter.Item>
        <Filter.Item label='适用系统' name='os' >
          <Select
            style={{ minWidth: 150 }}
            allowClear
            mode='multiple'
            placeholder='全部' size='middle'
            options={Object.keys(LIB_ENV).map((key: string) => ({ value: key, label: (LIB_ENV as any )[key] }))}
            onChange={(values: Array<string>) => onChange('os', values.join(','))} />
        </Filter.Item>
        {
          Object.keys(searchParams)
            .some((key: string) => (isArray(searchParams[key]) ? !isEmpty(searchParams[key]) : searchParams[key]))
          && (
            <Button type='link' onClick={onClear} className="ml-12" style={{ height: '36px' }}>清空过滤</Button>
          )
        }
      </Filter>
      {
        editable && (
          <Button type='primary' onClick={onAdd}>添加依赖</Button>
        )
      }
    </div>
  );
};

export default Search;
