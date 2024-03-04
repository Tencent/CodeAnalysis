// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Input, Form, Button, Tooltip, Checkbox } from 'coding-oa-uikit';
import AngleDown from 'coding-oa-uikit/lib/icon/AngleDown';
import AngleUp from 'coding-oa-uikit/lib/icon/AngleUp';
import Circulation from 'coding-oa-uikit/lib/icon/Circulation';
import SelectBorderless from '@src/components/select-borderless';
import Filter from '@src/components/filter';

import { CC_CHANGE_TYPE_OPTIONS } from '../../constants';

import style from '../style.scss';

const numberParams = ['change_type'];

interface SearchProps {
  href: string;
  searchParams: any;
  loading: boolean;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const [form] = Form.useForm();
  const { href, searchParams, loading, callback } = props;
  const [isMore, setIsMore] = useState(false);

  const initialValues = cloneDeep(searchParams);

  useEffect(() => {
    if (!loading) {
      // 表单数据格式化
      Object.entries(initialValues).forEach(([key, value]: [string, string]) => {
        if (numberParams.includes(key) && isString(value)) {
          initialValues[key] = value.split(',').map((item: string) => toNumber(item));
        }
      });
      const { file_path: filePath, last_modifier: lastModifier, ccn_gte: ccnGte, ccn_lte: ccnLte } = initialValues;

      // 如果高级搜索不为空，则展开
      if (!isMore && (
        filePath || lastModifier || ccnGte || ccnLte
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
    callback({});
  };

  return (
    <div className={style.ccSearchHeader}>
      <div className={style.fileHeader}>
        <div className={style.searchHeader}>
          <span className={style.title}>方法列表</span>
          <Tooltip title='切换到文件列表'>
            <Link to={href}><Circulation /></Link>
          </Tooltip>
        </div>
        <Checkbox
          className="mr-12"
          checked={searchParams?.change_type === '1,3' || searchParams?.change_type === '3,1'}
          onChange={(e: any) => onChange('change_type', e.target.checked ? '1,3' : '')}
        >
          <Tooltip title='增量问题：变更类型为新增和修改'>
            <span>仅查看增量问题</span>
          </Tooltip>
        </Checkbox>
        <Filter
          form={form}
          initialValues={initialValues}
        >
          <Filter.Item label='方法变更类型' name='change_type' >
            <SelectBorderless
              multiple
              allowClear
              placeholder='全部'
              data={CC_CHANGE_TYPE_OPTIONS}
              onChange={(value: any) => value && onChange('change_type', value.join(','))}
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
      </div>

      {
        isMore && (
          <Filter
            form={form}
            initialValues={initialValues}
            className="mt-xs"
          >
            <Filter.Item name='file_path' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='文件路径'
                onSearch={(value: string) => onChange('file_path', value)}
              />
            </Filter.Item>
            <Filter.Item name='last_modifier' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='最近修改人'
                onSearch={(value: string) => onChange('last_modifier', value)}
              />
            </Filter.Item>
            <Filter.Item name='ccn_gte' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='圈复杂度 >='
                onSearch={(value: string) => onChange('ccn_gte', value)}
              />
            </Filter.Item>
            <Filter.Item name='ccn_lte' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='圈复杂度 <='
                onSearch={(value: string) => onChange('ccn_lte', value)}
              />
            </Filter.Item>
          </Filter>
        )
      }
    </div>
  );
};

export default Search;
