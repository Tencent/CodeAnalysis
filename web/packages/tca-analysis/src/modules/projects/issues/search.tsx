// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import moment from 'moment';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Input, Form, Button, DatePicker } from 'coding-oa-uikit';
import AngleDown from 'coding-oa-uikit/lib/icon/AngleDown';
import AngleUp from 'coding-oa-uikit/lib/icon/AngleUp';

import SelectBorderless from '@src/components/select-borderless';
import Filter from '@src/components/filter';

import { RESOLUTIONS, SEVERITY } from '../constants';

import style from './style.scss';

const numberParams = ['state', 'severity', 'checkpackage'];
const arrayParams: any = [];
const timeParams = ['ci_time_gte', 'ci_time_lte'];

interface SearchProps {
  pkgs: any;
  searchParams: any;
  loading: boolean;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const [form] = Form.useForm();
  const { pkgs, searchParams, loading, callback } = props;
  const [isMore, setIsMore] = useState(false);

  const initialValues = cloneDeep(searchParams);

  useEffect(() => {
    if (!loading) {
      // 表单数据格式化
      Object.entries(initialValues).forEach(([key, value]: [string, string]) => {
        if (numberParams.includes(key) && isString(value)) {
          initialValues[key] = value.split(',').map((item: string) => toNumber(item));
        }

        if (arrayParams.includes(key) && isString(value)) {
          initialValues[key] = value.split(',');
        }

        if (timeParams.includes(key) && isString(value)) {
          initialValues[key] = moment(value);
        }
      });


      const {
        file_path: path,
        ci_time_gte: gte,
        ci_time_lte: lte,
        checkrule_display_name: name,
        checkpackage,
      } = initialValues;

      // 如果高级搜索不为空，则展开
      if (!isMore && (
        path || gte || lte || name || !isEmpty(checkpackage)
      )) {
        setIsMore(true);
      }
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
    <>
      <Filter
        form={form}
        initialValues={initialValues}
        className={style.issueFilter}
      >
        <Filter.Item label='问题级别' name='severity' >
          <SelectBorderless
            multiple
            allowClear
            placeholder='全部'
            data={Object.keys(SEVERITY).map((key: any) => ({ value: toNumber(key), text: SEVERITY[key] }))}
            onChange={(value: any) => value && onChange('severity', value.join(','))}
          />
        </Filter.Item>
        <Filter.Item label='状态' name='state' >
          <SelectBorderless
            multiple
            allowClear
            placeholder='全部'
            data={Object.keys(RESOLUTIONS).map((key: any) => ({ value: toNumber(key), text: RESOLUTIONS[key] }))}
            onChange={(value: any) => value && onChange('state', value.join(','))}
          />
        </Filter.Item>
        <Filter.Item name='author' >
          <Input.Search
            size='middle'
            style={{ width: '160px' }}
            placeholder='责任人'
            onSearch={(value: string) => onChange('author', value)}
          />
        </Filter.Item>
        <Filter.Item name='scan_open' >
          <Input.Search
            size='middle'
            style={{ width: '160px' }}
            placeholder='分析ID'
            onSearch={(value: string) => onChange('scan_open', value)}
          />
        </Filter.Item>

        <Button type='link' onClick={() => setIsMore(!isMore)} style={{ height: '36px' }}>
          高级搜索
        {isMore ? <AngleUp /> : <AngleDown />}
        </Button>

        {
          Object.keys(searchParams)
            .filter((key: string) => key !== 'ordering')
            .some((key: string) => (isArray(searchParams[key]) ? !isEmpty(searchParams[key]) : searchParams[key]))
          && (
            <Button type='link' onClick={onClear} className="ml-12" style={{ height: '36px' }}>清空过滤</Button>
          )
        }
      </Filter>

      {
        isMore && (
          <Filter
            form={form}
            initialValues={initialValues}
            className={style.issueFilter}
          >
            <Filter.Item label='规则包' name='checkpackage' >
              <SelectBorderless
                allowClear
                placeholder='全部'
                data={pkgs.map((item: any) => ({ value: item.id, text: item.name }))}
                onChange={(value: any) => value && onChange('checkpackage', value)}
              />
            </Filter.Item>
            <Filter.Item name='checkrule_real_name' >
              <Input.Search
                size='middle'
                style={{ width: '160px' }}
                placeholder='规则名称'
                onSearch={(value: string) => onChange('checkrule_real_name', value)}
              />
            </Filter.Item>

            <Filter.Item name='file_path' >
              <Input.Search
                size='middle'
                style={{ width: '160px' }}
                placeholder='所属文件'
                onSearch={(value: string) => onChange('file_path', value)}
              />
            </Filter.Item>
            <Filter.Item name='ci_time_gte' >
              <DatePicker
                showTime
                placeholder='版本引入开始时间'
                onChange={(date: any) => onChange('ci_time_gte', date ? date.format('YYYY-MM-DD HH:mm:ss') : '')}
              />
            </Filter.Item>
            <Filter.Item name='ci_time_lte' >
              <DatePicker
                showTime
                placeholder='版本引入结束时间'
                onChange={(date: any) => onChange('ci_time_lte', date ? date.format('YYYY-MM-DD HH:mm:ss') : '')}
              />
            </Filter.Item>
          </Filter>
        )
      }
    </>
  );
};

export default Search;
