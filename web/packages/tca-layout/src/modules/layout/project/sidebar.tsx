import React from 'react';
import { useParams } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import Repos from 'coding-oa-uikit/lib/icon/Repos';
import Scan from 'coding-oa-uikit/lib/icon/Scan';
import Api from 'coding-oa-uikit/lib/icon/Api';
import Group from 'coding-oa-uikit/lib/icon/Group';
import TeamOverview from 'coding-oa-uikit/lib/icon/TeamOverview';
// 项目内
import LayoutMenu from '@src/component/layout-menu';
import { getApiDocURL } from '@plat/util';

const SiderBar = () => {
  const { orgSid, name }: any = useParams();

  return <LayoutMenu breakpoint="lg"
    menus={[
      {
        icon: <Repos className='layoutMenuItemIcon' />,
        title: t('仓库登记'),
        link: `/t/${orgSid}/p/${name}/repos`,
        key: 'repos',
        regexMatch: /^\/t\/[^/]+\/p\/[^/]+\/repos/i,
      },
      {
        icon: <Scan className='layoutMenuItemIcon' />,
        title: t('代码分析'),
        key: 'code-analysis',
        childrens: [
          {
            title: t('分析项目'),
            link: `/t/${orgSid}/p/${name}/code-analysis/repos/projects`,
            key: 'projects',
            regexMatch: /(^\/t\/[^/]+\/p\/[^/]+\/code-analysis\/repos\/\d+\/projects)|(^\/t\/[^/]+\/p\/[^/]+\/code-analysis\/repos\/projects)/i,
          },
          {
            title: t('分析方案'),
            link: `/t/${orgSid}/p/${name}/code-analysis/repos/schemes`,
            key: 'schemes',
            regexMatch: /(^\/t\/[^/]+\/p\/[^/]+\/code-analysis\/repos\/\d+\/schemes)|(^\/t\/[^/]+\/p\/[^/]+\/code-analysis\/repos\/schemes)/i,
          },
        ],
      },
      {
        title: '',
        key: 'divider-1',
        divider: true,
      },
      {
        icon: <TeamOverview className='layoutMenuItemIcon' />,
        title: t('项目概览'),
        link: `/t/${orgSid}/p/${name}/profile`,
        key: 'profile',
        regexMatch: /^\/t\/[^/]+\/p\/[^/]+\/profile/i,
      },
      {
        icon: <Group className='layoutMenuItemIcon' />,
        title: t('项目成员'),
        link: `/t/${orgSid}/p/${name}/group`,
        key: 'group',
        regexMatch: /^\/t\/[^/]+\/p\/[^/]+\/group/i,
      },
      {
        title: '',
        key: 'divider-2',
        divider: true,
      },
      {
        icon: <Api className='layoutMenuItemIcon' />,
        title: t('开放平台'),
        link: getApiDocURL(),
        key: 'docs',
        open: true,
      },
    ]}
  />;
};

export default SiderBar;
