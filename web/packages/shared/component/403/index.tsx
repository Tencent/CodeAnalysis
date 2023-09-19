import React from 'react';
import { useHistory } from 'react-router-dom';
import { Result, Button } from 'coding-oa-uikit';
import { ResultProps } from 'coding-oa-uikit/lib/result';

const Page403 = (props: Omit<ResultProps, 'status'>) => {
  const history = useHistory();
  const {
    style = { marginTop: 60 },
    title = '403',
    subTitle = '抱歉，您暂时没有权限访问该页面',
    extra = <>
      <Button type="primary" onClick={() => {
        history.replace('/');
      }} >返回首页</Button>
    </>,
    ...rest
  } = props;
  return <Result status="403" style={style} title={title} subTitle={subTitle} extra={extra} {...rest} />;
};

export default Page403;
