import React, { useEffect } from 'react';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Form, Button, Input, Select } from 'coding-oa-uikit';

// 项目内
import Filter from '@src/components/filter';

// 模块内
import { ORG_STATUS_OPTIONS } from './constants';

const numberParams: Array<string> = ['status'];
const arrayParams: Array<string> = [];

interface SearchProps {
  searchParams: any;
  loading: boolean;
  callback: (params: any) => void;
}

const Search = ({ searchParams, loading, callback }: SearchProps) => {
  const [form] = Form.useForm();
  const initialValues = cloneDeep(searchParams);

  Object.entries(initialValues).map(([key, value]: [string, string]) => {
    if (numberParams.includes(key) && isString(value)) {
      initialValues[key] = value.split(',').map((item: string) => toNumber(item));
    }

    if (arrayParams.includes(key) && isString(value)) {
      initialValues[key] = value.split(',');
    }
    return [key, value];
  });

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
    callback({
      name: '',
      status: '',
    });
  };

  return (
    <Filter form={form} style={{ margin: '8px 0' }} initialValues={initialValues}>
      <Filter.Item label="状态" name="status">
        <Select
          style={{ width: 120 }}
          placeholder='全部' size='middle'
          options={ORG_STATUS_OPTIONS}
          onChange={value => onChange('status', value)} />
      </Filter.Item>
      <Filter.Item label="" name="name">
        <Input.Search
          size="middle"
          placeholder="团队名称"
          onSearch={value => onChange('name', value)}
        />
      </Filter.Item>
      {Object.keys(searchParams).some((key: string) => (
        isArray(searchParams[key]) ? !isEmpty(searchParams[key]) : searchParams[key]))
        && (
          <Button type="link" onClick={onClear} style={{ height: '36px' }}>
            清空过滤
          </Button>
        )}
    </Filter>
  );
};

export default Search;
