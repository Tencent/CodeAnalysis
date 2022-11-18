/**
 * 过滤筛选组件
 */
import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { isEmpty, pick } from 'lodash';
import classnames from 'classnames';
import { Input, Form, Select, DatePicker, Button, Checkbox } from 'coding-oa-uikit';
import AngleDown from 'coding-oa-uikit/lib/icon/AngleDown';
import AngleUp from 'coding-oa-uikit/lib/icon/AngleUp';

import { getURLPathByFilterParams } from '../../util/route';
import { FilterField, Filter as FilterParams } from '../../util/types';
import Filter from '../filter';
import s from './style.scss';

/** 判断是否存在不为空的筛选参数 */
const isExistSearchParam = (params: FilterParams) => Object.keys(params)
  .some((key: string) => typeof params[key] === 'number' || !isEmpty(params[key]));

/** search 组件 表单类型 */
export type SearchFormFieldType = 'input' | 'select' | 'datepicker' | 'checkbox' | 'multiselect';

/** search 组件表单字段类型 */
export interface SearchFormField extends FilterField {
  /** 表单类型 */
  formType: SearchFormFieldType;
  /** 表单value */
  formValue?: string | number;
  /** form item 名称  */
  label?: string;
  /** 表单 placeholder */
  placeholder?: string;
  /** select options，仅type为select时生效 */
  options?: any[]
  /** 表单样式 */
  style?: React.CSSProperties
}

interface SearchProps {
  /** 一级筛选字段 */
  fields: SearchFormField[],
  /** 高级筛选字段 */
  moreFields?: SearchFormField[],
  /** 筛选参数，传入参数 */
  searchParams: FilterParams;
  /** 筛选请求加载中 */
  loading: boolean;
  /** 筛选回调 */
  callback?: (params: any) => void;
  /** 是否开启路由跳转，默认开启 */
  route?: boolean;
  /** 筛选组件class */
  className?: string;
  /** 筛选组件style */
  style?: React.CSSProperties;
  /** 首行额外内容 */
  extraContent?: React.ReactNode
}

const Search = ({
  fields, moreFields, searchParams, loading, callback,
  className, style, extraContent, route = true,
}: SearchProps) => {
  const [form] = Form.useForm();
  const [more, setMore] = useState(false);
  const history = useHistory();

  useEffect(() => {
    // loading 结束后reset form
    if (!loading) {
      form.resetFields();
      // 判断是否展开高级筛选
      if (moreFields) {
        const fieldNames = moreFields.map(field => field.name);
        if (isExistSearchParam(pick(searchParams, fieldNames))) {
          setMore(true);
        }
      }
    }
  }, [loading]);

  // 筛选路由跳转处理，仅当route为true时生效
  const onRouteHandle = (params: FilterParams) => {
    if (route) {
      const url = getURLPathByFilterParams(moreFields ? fields.concat(moreFields) : fields, params);
      history.push(url);
    }
  };

  const onChange = (key: string, value: any) => {
    const params = {
      ...searchParams,
      [key]: value,
      offset: null,
    };
    onRouteHandle(params);
    callback?.(params);
  };

  const onClear = () => {
    const params: FilterParams = {};
    // 将筛选入参清空
    Object.keys(searchParams).forEach((key) => {
      params[key] = '';
    });
    form.setFieldsValue(params);
    onRouteHandle(params);
    callback?.(params);
  };

  const getItem = (field: SearchFormField) => {
    switch (field.formType) {
      case 'input':
        return <Input.Search
          size='middle'
          style={{ width: 150, ...field.style }}
          placeholder={field.placeholder}
          onSearch={(value: string) => onChange(field.name, value)}
        />;
      case 'select':
        return <Select
          style={{ width: 150, ...field.style }}
          allowClear
          placeholder={field.placeholder || '全部'} size='middle'
          options={field.options}
          onChange={value => onChange(field.name, value)} />;
      case 'multiselect':
        return <Select
          mode='multiple'
          showArrow
          style={{ width: 150, ...field.style }}
          allowClear
          placeholder={field.placeholder || '全部'} size='middle'
          options={field.options}
          onChange={value => onChange(field.name, value)} />;
      case 'datepicker':
        return <DatePicker
          showTime
          placeholder={field.placeholder}
          onChange={(date: any) => onChange(field.name, date ? date.format('YYYY-MM-DD HH:mm:ss') : '')}
        />;
      case 'checkbox':
        return <Checkbox onChange={e => onChange(field.name, e.target.checked ? field.formValue : '')}>{field.placeholder}</Checkbox>;
      default:
        throw new Error('field type error');
    }
  };

  return <div className={classnames(s.search, className)} style={style}>
    <div className={classnames(s.searchFirst)}>
      <Filter
        form={form}
        initialValues={searchParams}
        className={s.searchContent}
      >
        {fields.map(field => <Filter.Item key={field.name}
          label={field.label ? <span className='mr-sm'>{field.label}</span> : ''}
          name={field.name}
          valuePropName={field.formType === 'checkbox' ? 'checked' : 'value'}>
          {getItem(field)}
        </Filter.Item>)}
        {moreFields
          && <Button type='link' onClick={() => setMore(!more)} style={{ height: '36px' }}>
            高级搜索
            {more ? <AngleUp /> : <AngleDown />}
          </Button>
        }
        {
          isExistSearchParam(searchParams) && (
            <Button type='link' onClick={onClear} className="ml-12" style={{ height: '36px' }}>清空过滤</Button>
          )
        }
      </Filter>
      {extraContent}
    </div>
    {
      moreFields && more && (
        <Filter
          form={form}
          initialValues={searchParams}
          className={s.searchContent}
        >
          {moreFields.map(field => <Filter.Item key={field.name} label={field.label ? <span className='mr-sm'>{field.label}</span> : ''} name={field.name} >
            {getItem(field)}
          </Filter.Item>)}
        </Filter>
      )
    }
  </div>;
};

export default Search;

