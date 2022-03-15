import React, { useEffect } from 'react';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Form, Button, Input, Select } from 'coding-oa-uikit';

// 项目内
import Filter from '@src/components/filter';

// 模块内

const numberParams: Array<string> = ['state', 'result'];
const arrayParams: Array<string> = [];

interface SearchProps {
  searchParams: any;
  loading: boolean;
  callback: (params: any) => void;
  tagOptions: any[]
}

const Search = ({ searchParams, loading, callback, tagOptions }: SearchProps) => {
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
    const formatValue = value === undefined ? '' : value;
    callback({
      ...searchParams,
      [key]: formatValue,
    });
  };

  const onClear = () => {
    form.resetFields();
    callback({
      name: '',
      manager: '',
      exec_tags: ''
    });
  };

  return (
    <Filter form={form} style={{ margin: '8px 0' }} initialValues={initialValues}>
      <Filter.Item label="" name="name">
        <Input.Search
          size="middle"
          placeholder="节点名称"
          onSearch={value => onChange('name', value)}
        />
      </Filter.Item>
      <Filter.Item label="" name="manager">
        <Input.Search
          size="middle"
          placeholder="负责人"
          onSearch={value => onChange('manager', value)}
        />
      </Filter.Item>
      <Filter.Item label="所属标签" name="exec_tags">
        <Select
          style={{ width: 200 }}
          allowClear
          placeholder='全部' size='middle'
          options={tagOptions}
          onChange={value => onChange('exec_tags', value)} />
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
