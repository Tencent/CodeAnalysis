import React, { useEffect } from 'react';
import { toNumber, isString, isEmpty, isArray, cloneDeep } from 'lodash';
import { Form, Button, Input, Select } from 'coding-oa-uikit';

// 项目内
// import SelectBorderless from '@src/components/select-borderless';
import Filter from '@src/components/filter';

// 模块内
// import { RUN_TYPE_OPTIONS, STATE_OPTIONS, RESULT_OPTIONS } from './constants';
import { STATE_OPTIONS, RESULT_OPTIONS } from './constants';

const numberParams: Array<string> = ['state', 'result'];
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
    const formatValue = value === undefined ? '' : value;
    callback({
      ...searchParams,
      [key]: formatValue,
    });
  };

  const onClear = () => {
    form.resetFields();
    callback({
      run_type: '',
      state: '',
      result: '',
      // organization: '',
      // project_team: '',
      // project: '',
      repo: '',
    });
  };

  return (
    <Filter form={form} style={{ margin: '8px 0' }} initialValues={initialValues}>
      {/* <Filter.Item label="触发类型" name="run_type">
      <Select
          style={{ width: 120 }}
          allowClear
          placeholder='全部' size='middle'
          options={RUN_TYPE_OPTIONS}
          onChange={value => onChange('run_type', value)} />
            </Filter.Item> */}
      <Filter.Item label="执行状态" name="state">
        <Select
          style={{ width: 120 }}
          allowClear
          placeholder='全部' size='middle'
          options={STATE_OPTIONS}
          onChange={value => onChange('state', value)} />
      </Filter.Item>
      <Filter.Item label="执行结果" name="result">
        <Select
          style={{ width: 120 }}
          allowClear
          placeholder='全部' size='middle'
          options={RESULT_OPTIONS}
          onChange={value => onChange('result', value)} />
      </Filter.Item>
      <Filter.Item label="" name="repo">
        <Input.Search
          size="middle"
          placeholder="代码库 ID"
          onSearch={value => onChange('repo', value)}
        />
      </Filter.Item>
      {/* <Filter.Item label="" name="organization">
                <Input.Search
                    size="middle"
                    placeholder="团队 ID"
                    onSearch={value => onChange('organization', value)}
                />
            </Filter.Item> */}
      {/* <Filter.Item label="" name="project_team">
                <Input.Search
                    size="middle"
                    placeholder="项目 ID"
                    onSearch={value => onChange('project_team', value)}
                />
            </Filter.Item>
            <Filter.Item label="" name="project">
                <Input.Search
                    size="middle"
                    placeholder="分析任务 ID"
                    onSearch={value => onChange('project', value)}
                />
            </Filter.Item> */}
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
