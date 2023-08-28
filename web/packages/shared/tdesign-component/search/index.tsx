/**
 * 过滤筛选组件
 */
import React, { useState, useEffect, useRef } from 'react';
import { useHistory } from 'react-router-dom';
import { get, isEmpty, pick } from 'lodash';
import classnames from 'classnames';
import { Button, Checkbox, Input, Select, DatePicker, Loading, Row, Col, DateRangePicker, Form } from 'tdesign-react';
import { ChevronDownIcon, ChevronUpIcon, ClearIcon } from 'tdesign-icons-react';
import { getURLPathByFilterParams } from '../../util/route';
import { FilterField, Filter as FilterParams } from '../../util/types';
import { formatDate } from '../../util';
import s from './style.scss';

const { FormItem } = Form;

/** 判断是否存在不为空的筛选参数 */
const isExistSearchParam = (params: FilterParams) => Object.keys(params)
  .some((key: string) => typeof params[key] === 'number' || !isEmpty(params[key]) || params[key] === true);

/** search 组件 表单类型 */
export type SearchFormFieldType = 'input' | 'select' | 'datepicker' | 'checkbox' | 'multiselect' | 'rangepicker';

/** search 组件表单字段类型 */
export interface SearchFormField extends FilterField {
  /** 表单类型 */
  formType: SearchFormFieldType;
  /** 表单value */
  defaultValue?: string | number;
  /** form item 名称  */
  label?: string;
  /** 表单 placeholder */
  placeholder?: string;
  /** 表单 加载状态 */
  loading?: boolean;
  /** select options，仅type为select时生效 */
  options?: any[];
  /** select 可选择，仅type为select时生效 */
  keys?: any;
  /** select 可选择，仅type为select时生效 */
  filterable?: boolean;
  /** 表单样式 */
  style?: React.CSSProperties;
}

interface SearchProps {
  /** 一级筛选字段 */
  fields: SearchFormField[],
  /** 高级筛选字段 */
  moreFields?: SearchFormField[],
  /** 筛选参数，传入参数 */
  searchParams: FilterParams;
  /** 筛选请求加载中 */
  loading?: boolean;
  /** 筛选回调 */
  callback?: (params: any) => void;
  /** 是否开启路由跳转，默认开启 */
  route?: boolean;
  /** 筛选组件class */
  className?: string;
  /** 筛选组件style */
  style?: React.CSSProperties;
  /** 首行额外内容 */
  extraContent?: React.ReactNode;
  /** 尾部额外内容 */
  appendContent?: React.ReactNode;
  /** 筛选项 */
  filters?: FilterField[];
  /** 默认筛选键值对 */
  defaultValues?: any;
}

const formLayout = {
  flex: '0 1 auto',
};

const Search = ({
  fields, moreFields, searchParams, loading = false, callback,
  className, style, extraContent, route = true, filters, appendContent,
  defaultValues,
}: SearchProps) => {
  const [more, setMore] = useState(false);
  const history = useHistory();
  const formRef = useRef<any>(null);

  useEffect(() => {
    if (!loading) {
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
      const filterFields = moreFields ? fields.concat(moreFields) : fields;
      const url = getURLPathByFilterParams(filters ? filters : filterFields, params);
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

  const onRangeChange = (key: string, range: any) => {
    const params = {
      ...searchParams,
      [`${key}_gte`]: range[0],
      [`${key}_lte`]: range[1],
      offset: null,
    };
    onRouteHandle(params);
    callback?.(params);
  };

  const onClear = () => {
    const params: FilterParams = {};
    // 将筛选入参清空
    Object.keys(searchParams).forEach((key) => {
      params[key] = [];
      if (key.endsWith('_lte') || key.endsWith('_gte')) {
        params[key.substring(0, key.length - 4)] = '';
      }
    });
    onRouteHandle({ ...params, ...defaultValues });
    callback?.({ ...params, ...defaultValues });
    formRef.current?.setFieldsValue?.({ ...params, ...defaultValues });
  };

  const getItem = (field: SearchFormField) => {
    switch (field.formType) {
      case 'input':
        return <Input
          clearable={!field.defaultValue}
          style={{ width: 150, ...field.style }}
          placeholder={field.placeholder}
          onEnter={value => onChange(field.name, value)}
          onClear={() => onChange(field.name, '')} />;
      case 'select':
        return <Select
          style={{ width: 150, ...field.style }}
          filterable={field.filterable}
          loading={field.loading}
          clearable={!field.defaultValue}
          placeholder={field.placeholder || '全部'}
          options={field.options}
          keys={field.keys}
          onChange={value => onChange(field.name, value)} />;
      case 'multiselect':
        return <Select
          multiple
          style={{ width: 150, ...field.style }}
          filterable={field.filterable}
          loading={field.loading}
          placeholder={field.placeholder || '全部'}
          options={field.options}
          keys={field.keys}
          onChange={value => onChange(field.name, value)} />;
      case 'datepicker':
        return <DatePicker
          style={{ width: 150, ...field.style }}
          placeholder={field.placeholder}
          onChange={(date: any) => onChange(field.name, date ? formatDate(date) : '')}
        />;
      case 'rangepicker':
        return <DateRangePicker
          style={{ width: 300, ...field.style }}
          placeholder={field.placeholder}
          onChange={(dateRange: any) => onRangeChange(field.name, dateRange)}
        />;
      case 'checkbox':
        return <Checkbox onChange={checked => onChange(field.name, checked)}>{field.placeholder}</Checkbox>;
      default:
        throw new Error('field type error');
    }
  };

  const getInitData = (field: SearchFormField) => {
    switch (field.formType) {
      case 'multiselect':
        return get(searchParams, field.name) || field.defaultValue || [];
      case 'rangepicker':
        return [get(searchParams, `${field.name}_gte`), get(searchParams, `${field.name}_lte`)] || field.defaultValue || [];
      default:
        return get(searchParams, field.name) || field.defaultValue || null;
    }
  };

  return (
    <Loading size="small" loading={loading} showOverlay>
      <div className={classnames(s.search, className)} style={style}>
        <Form
          className={s.searchContent}
          labelWidth='auto'
          style={{ width: '100%' }}
          ref={formRef}
        >
          <Row gutter={[16, 8]}>
            {fields
              .map(field => (<Col key={field.name} {...formLayout}>
                <FormItem
                  key={field.name}
                  label={field.label}
                  name={field.name}
                  initialData={getInitData(field)}
                >
                  {getItem(field)}
                </FormItem>
              </Col>))}
            {!isEmpty(moreFields) && !loading
              && <Col>
                <Button
                  theme="primary"
                  variant="text"
                  onClick={() => setMore(!more)}
                  style={{ height: '32px' }}
                  icon={more ? <ChevronUpIcon /> : <ChevronDownIcon />}
                >
                  高级搜索
                </Button>
              </Col>
            }
            {isExistSearchParam(searchParams)
              && <Col>
                <Button
                  theme='danger'
                  variant="text"
                  onClick={onClear}
                  style={{ height: '32px' }}
                  icon={<ClearIcon />}
                >
                  清空过滤
                </Button>
              </Col>
            }
            {appendContent && <Col>{appendContent}</Col>}
          </Row>
          {moreFields && more && <Row gutter={[16, 8]} style={{ marginTop: '8px' }}>
            {moreFields
              .map(field => <Col key={field.name} {...formLayout}>
                <FormItem
                  key={field.name}
                  label={field.label}
                  name={field.name}
                  initialData={getInitData(field)}
                >
                  {getItem(field)}
                </FormItem>
              </Col>)}
          </Row>}
        </Form>
        {extraContent}
      </div>
    </Loading>);
};

export default Search;

