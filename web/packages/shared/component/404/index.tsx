import React from 'react';
import { useHistory } from 'react-router-dom';
import { Result, Button } from 'coding-oa-uikit';
import { ResultProps } from 'coding-oa-uikit/lib/result';


const Page404 = (props: Omit<ResultProps, 'status'>) => {
  const history = useHistory();
  const {
    style = { marginTop: 60 },
    title = '404',
    subTitle = '抱歉，您访问的页面不存在，请确认路由是否准确',
    extra = <>
      <Button type="primary" onClick={() => {
        history.replace('/');
      }} >返回首页</Button>
    </>,
    ...rest
  } = props;
  return <Result status="404" style={style} title={title} subTitle={subTitle} extra={extra} {...rest} />;
};

export default Page404;
