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

import { CC_CHANGE_TYPE_OPTIONS, CC_STATE } from '../../constants';

import commonStyle from '../style.scss';

const numberParams = ['state', 'change_type'];

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

      const {
        file_path: filePath,
        over_cc_func_count_gte: overCCFuncCountGte,
        over_cc_func_count_lte: overCCFuncCountLte,
        over_cc_avg_gte: overCCAvgGte,
        over_cc_avg_lte: overCCAvgLte,
      } = initialValues;

      // 如果高级搜索不为空，则展开
      if (!isMore && (
        filePath || overCCFuncCountGte || overCCFuncCountLte || overCCAvgGte || overCCAvgLte
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
    <div className={commonStyle.ccSearchHeader}>
      <div className={commonStyle.fileHeader}>
        <div className={commonStyle.searchHeader}>
          <span className={commonStyle.title}>文件列表</span>
          <Tooltip title='切换到方法列表'>
            <Link to={href}><Circulation /></Link>
          </Tooltip>
        </div>
        <Checkbox
          className="mr-xs"
          checked={initialValues.worse}
          onChange={(e: any) => onChange('worse', e.target.checked || '')}
        >
          仅查看恶化文件
        </Checkbox>
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
          <Filter.Item label='状态' name='state' >
            <SelectBorderless
              allowClear
              placeholder='全部'
              data={CC_STATE}
              onChange={(value: any) => value && onChange('state', value)}
            />
          </Filter.Item>
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
            <Filter.Item name='last_modifier' >
              <Input.Search
                size='middle'
                style={{ width: '140px' }}
                placeholder='最近修改人'
                onSearch={(value: string) => onChange('last_modifier', value)}
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
            <Filter.Item name='over_cc_func_count_gte' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='超标方法个数 >='
                onSearch={(value: string) => onChange('over_cc_func_count_gte', value)}
              />
            </Filter.Item>
            <Filter.Item name='over_cc_func_count_lte' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='超标方法个数 <='
                onSearch={(value: string) => onChange('over_cc_func_count_lte', value)}
              />
            </Filter.Item>
            <Filter.Item name='over_cc_avg_gte' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='平均圈复杂度 >='
                onSearch={(value: string) => onChange('over_cc_avg_gte', value)}
              />
            </Filter.Item>
            <Filter.Item name='over_cc_avg_lte' >
              <Input.Search
                size='middle'
                style={{ width: '164px' }}
                placeholder='平均圈复杂度 <='
                onSearch={(value: string) => onChange('over_cc_avg_lte', value)}
              />
            </Filter.Item>
          </Filter>
        )
      }
    </div>
  );
};

export default Search;
