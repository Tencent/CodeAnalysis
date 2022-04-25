/**
 * 规则列表搜索栏
 */
import React, { useEffect } from 'react';
import { cloneDeep, isArray, isEmpty, isString, toNumber, get } from 'lodash';
import { Button, Form, Input, Checkbox, Select } from 'coding-oa-uikit';
// import SelectBorderless from '@src/components/select-borderless';
import Filter from '@src/components/filter';
import { TOOL_STATUS } from './constants';

import style from './style.scss';

const numberParams = ['status'];

interface SearchProps {
  orgSid: string;
  loading: boolean;
  searchParams: any;
  editable: boolean;
  onAdd: () => void;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const { searchParams, loading, editable, onAdd, callback } = props;
  const [form] = Form.useForm();
  const initialValues = cloneDeep(searchParams);

  useEffect(() => {
    if (!loading) {
      // 表单数据格式化
      Object.entries(initialValues).map(([key, value]: [string, string]) => {
        if (numberParams.includes(key) && isString(value)) {
          initialValues[key] = value.split(',').map((item: string) => toNumber(item));
        }
        return [key, value];
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
    callback({});
  };

  return (
    <div className={style.filter}>
      <Filter
        form={form}
        initialValues={{
          ...initialValues,
          scope: initialValues.scope === '3',
        }}
      >
        <Filter.Item name='display_name' >
          <Input.Search
            size='middle'
            style={{ width: '160px' }}
            placeholder='工具名称'
            onSearch={(value: string) => onChange('display_name', value)}
          />
        </Filter.Item>
        <Filter.Item label='工具状态' name='status' >
          <Select
            style={{ width: 120 }}
            allowClear
            placeholder='全部' size='middle'
            options={Object.keys(TOOL_STATUS).map(item => ({ value: item, label: get(TOOL_STATUS, item) }))}
            onChange={value => onChange('status', value)} />
        </Filter.Item>
        {/* <Filter.Item label='工具状态' name='status' >
          <SelectBorderless
            allowClear
            placeholder='全部'
            data={Object.keys(TOOL_STATUS).map(item => ({ value: item, text: TOOL_STATUS[item] }))}
            onChange={(value: any) => onChange('status', value)}
          />
        </Filter.Item> */}
        <Filter.Item name='scope' valuePropName='checked'>
          <Checkbox onChange={e => onChange('scope', e.target.checked ? 3 : '')}>仅查看自定义工具</Checkbox>
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
          <Button type='primary' onClick={onAdd}>创建工具</Button>
        )
      }
    </div>
  );
};

export default Search;
