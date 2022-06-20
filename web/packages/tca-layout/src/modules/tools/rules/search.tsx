/**
 * 规则列表搜索栏
 */
import React, { useEffect } from 'react';
import { cloneDeep, isArray, isEmpty, isString, toNumber } from 'lodash';
import { Button, Form, Input, Select } from 'coding-oa-uikit';
import Filter from '@src/components/filter';

import style from '../detail.scss';

const numberParams = ['category', 'severity'];
const arrayParams = ['language_name'];

interface SearchProps {
  orgSid: string;
  toolId: number;
  loading: boolean;
  filters: any;
  searchParams: any;
  editable: boolean;
  addRule: () => void;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const { filters, searchParams, loading, editable, addRule, callback } = props;
  const [form] = Form.useForm();
  const { severity = [], category = [], language_name: languageName = [] } = filters;
  const initialValues = cloneDeep(searchParams);

  useEffect(() => {
    if (!loading) {
      // 表单数据格式化
      Object.entries(initialValues).map(([key, value]: [string, string]) => {
        if (numberParams.includes(key) && isString(value)) {
          initialValues[key] = value.split(',').map((item: string) => toNumber(item));
        }

        if (arrayParams.includes(key) && isString(value)) {
          initialValues[key] = value.split(',');
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
        initialValues={initialValues}
      // className={style.issueFilter}
      >
        <Filter.Item label="严重级别" name="severity">
          <Select
            mode='multiple'
            style={{ minWidth: 100 }}
            allowClear
            placeholder='全部' size='middle'
            options={severity.map((item: any) => ({
              value: item.value,
              label: `${item.display_name} (${item.count})`,
            }))}
            onChange={(value: []) => onChange('severity', value.join(','))} />
        </Filter.Item>
        <Filter.Item label="规则分类" name="category">
          <Select
            mode='multiple'
            style={{ minWidth: 100 }}
            allowClear
            placeholder='全部' size='middle'
            options={category.map((item: any) => ({
              value: item.value,
              label: `${item.display_name} (${item.count})`,
            }))}
            onChange={(value: []) => onChange('category', value.join(','))} />
        </Filter.Item>
        <Filter.Item label="适用语言" name="language_name">
          <Select
            mode='multiple'
            style={{ minWidth: 100 }}
            allowClear
            placeholder='全部' size='middle'
            options={languageName.map((item: any) => ({
              value: item.value,
              label: `${item.display_name} (${item.count})`,
            }))}
            onChange={(value: []) => onChange('language_name', value.join(','))} />
        </Filter.Item>
        <Filter.Item label="规则状态" name="disable">
          <Select
            style={{ minWidth: 100 }}
            allowClear
            placeholder='全部' size='middle'
            options={[{ value: 'false', label: '可用' }, { value: 'true', label: '不可用' }]}
            onChange={(value: []) => onChange('disable', value)} />
        </Filter.Item>
        {/* <Filter.Item label='严重级别' name='severity' >
          <SelectBorderless
            multiple
            allowClear
            placeholder='全部'
            data={severity.map((item: any) => ({
              value: item.value,
              text: `${item.display_name} (${item.count})`,
            }))}
            onChange={(value: any) => value && onChange('severity', value.join(','))}
          />
        </Filter.Item>
        <Filter.Item label='规则分类' name='category' >
          <SelectBorderless
            multiple
            allowClear
            placeholder='全部'
            data={category.map((item: any) => ({
              value: item.value,
              text: `${item.display_name} (${item.count})`,
            }))}
            onChange={(value: any) => value && onChange('category', value.join(','))}
          />
        </Filter.Item>
        <Filter.Item label='适用语言' name='language_name' >
          <SelectBorderless
            multiple
            allowClear
            placeholder='全部'
            data={language_name.map((item: any) => ({
              value: item.value,
              text: `${item.display_name} (${item.count})`,
            }))}
            onChange={(value: any) => value && onChange('language_name', value.join(','))}
          />
        </Filter.Item>
        <Filter.Item label='规则状态' name='disable' >
          <SelectBorderless
            multiple
            allowClear
            placeholder='全部'
            data={[{ value: 'false', text: '可用' }, { value: 'true', text: '不可用' }]}
            onChange={(value: any) => value && onChange('disable', value.join(','))}
          />
        </Filter.Item> */}
        <Filter.Item name='display_name' >
          <Input.Search
            size='middle'
            style={{ width: '160px' }}
            placeholder='规则名'
            onSearch={(value: string) => onChange('display_name', value)}
          />
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
          <Button type='primary' onClick={addRule}>添加规则</Button>
        )
      }
    </div>
  );
};

export default Search;
