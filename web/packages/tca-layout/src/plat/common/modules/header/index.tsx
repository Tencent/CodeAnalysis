import React from 'react';
import { useParams } from 'react-router-dom';
import LayoutHeader from '@tencent/micro-frontend-shared/tca/component/layout-header';

// 模块内
import { getTeamsRouter, getHomeRouter } from '@src/utils/getRoutePath';
import RightZone from './right-zone';
import Enterprise from './enterprise';

const Header = () => {
  const { orgSid }: any = useParams();

  return <LayoutHeader
    linkTo={orgSid ? getTeamsRouter() : getHomeRouter()}
    leftContent={
      orgSid && <>
        <span className='text-grey-7'>|</span>
        <Enterprise />
      </>
    }
    rightContent={<RightZone />} />;
};
export default Header;
