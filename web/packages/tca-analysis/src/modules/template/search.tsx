import React, { useEffect } from 'react';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Input, Form, Button } from 'coding-oa-uikit';

import Filter from '@src/components/filter';
import style from './style.scss';

const numberParams = ['state', 'severity'];
const arrayParams = ['author'];

interface SearchProps {
  searchParams: any;
  loading: boolean;
  createTmpl: () => void;
  callback: (params: any) => void;
}

const Search = (props: SearchProps) => {
  const [form] = Form.useForm();
  const { searchParams, loading, createTmpl, callback } = props;

  const initialValues = cloneDeep(searchParams);

  Object.entries(initialValues).forEach(([key, value]: [string, string]) => {
    if (numberParams.includes(key) && isString(value)) {
      initialValues[key] = value.split(',').map((item: string) => toNumber(item));
    }

    if (arrayParams.includes(key) && isString(value)) {
      initialValues[key] = value.split(',');
    }
  });

  useEffect(() => {
    !loading && form.resetFields();
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
        <div className={style.search}>
            <Filter form={form} style={{ margin: '12px 0' }} initialValues={initialValues}>
                <Filter.Item label="" name="name">
                    <Input.Search
                        size="middle"
                        style={{ width: '160px' }}
                        placeholder="搜索模板名称"
                        onSearch={value => onChange('name', value)}
                    />
                </Filter.Item>
                {
                Object.keys(searchParams).some((key: string) => (isArray(searchParams[key])
                  ? !isEmpty(searchParams[key])
                  : searchParams[key])) && (
                    <Button type="link" onClick={onClear} style={{ height: '36px' }}>
                        清空过滤
                    </Button>
                )}
            </Filter>
            <Button type="primary" onClick={createTmpl}>
                创建模板
            </Button>
        </div>
  );
};

export default Search;
