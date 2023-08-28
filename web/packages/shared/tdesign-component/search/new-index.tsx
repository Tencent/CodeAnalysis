// td 新筛选 组件
import React, { useMemo, useState } from 'react';
import classnames from 'classnames';
import { Form, SubmitContext, Loading, Row, Col, Button } from 'tdesign-react';
import { ChevronUpCircleIcon, ChevronDownCircleIcon, CloseCircleFilledIcon } from 'tdesign-icons-react';

import { SearchFormField, SearchFormFieldComponent } from './types';

// import { Filter as FilterParams } from '../../util/types';

import s from './style.scss';
import { omit } from 'lodash';
// import { getURLSearch } from '../../util';

export * from './types';

const { FormItem } = Form;

/** 判断是否存在不为空的筛选参数 */
// const isExistSearchParam = (params: FilterParams) => Object.keys(params)
//   .some((key: string) => typeof params[key] === 'number' || !isEmpty(params[key]) || params[key] === true);


interface FormItemComponentProps {
  field: SearchFormField
}

const FormItemComponent = ({ field }: FormItemComponentProps) => {
  const options = omit(field, ['formType', 'label', 'type', 'name']);
  const Component = SearchFormFieldComponent[field.formType];
  return <FormItem name={field.name}>
    <Component style={{ width: '100%' }} clearable prefixIcon={<span className={s.formItemLabel}>{field.label}: </span>} {...options} />
  </FormItem>;
};

interface SearchProps {
  /** 加载状态 */
  loading?: boolean;
  /** Form className */
  className?: string
  /** 操作项 width */
  actionWidth?: number;
  /** Row, Action Space gutter, default [16, 8] */
  gutter?: number[]
  /** 筛选项 */
  fields: SearchFormField[],
}

const Search = (props: SearchProps) => {
  const { loading = false, className, gutter = [16, 8], fields } = props;
  const [more] = useState(false);
  const [form] = Form.useForm();
  const onSubmit = (e: SubmitContext) => {
    if (e.validateResult === true) {
      console.log(e.fields);
    }
  };
  const onReset = () => {
    console.log('reset');
    form.reset();
  };

  const formItems = useMemo(() => fields.map(field => <Col key={field.name} span={6} md={4} xl={3} xxl={2}>
    <FormItemComponent field={field} />
  </Col>), [fields]);

  return <Loading size='small' loading={loading} showOverlay>
    <div className={classnames(s.searchForm, className)}>
      <Row gutter={gutter}>
        <Col flex="1">
          <Form className={s.formContent} onSubmit={onSubmit} onReset={onReset} labelWidth={80} colon >
            <Row gutter={gutter}>
              {formItems}
            </Row>
            <div className={s.formContentOp} >
              <Button className={classnames(s.formContentBtn, s.more)} theme="primary" variant='text' shape='square' icon={more ? <ChevronUpCircleIcon /> : <ChevronDownCircleIcon />} />
              <Button className={classnames(s.formContentBtn, s.clear)} type='reset' theme='danger' variant='text' shape='square' icon={<CloseCircleFilledIcon />} />
            </div>
          </Form>
        </Col>
        <Col flex="240px">
        </Col>
      </Row>
    </div>

  </Loading>;
};

export default Search;
