import React from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import Panel from 'coding-oa-uikit/lib/icon/Panel';
import Group from 'coding-oa-uikit/lib/icon/Group';
import Project from 'coding-oa-uikit/lib/icon/Project';
import Api from 'coding-oa-uikit/lib/icon/Api';
import TeamOverview from 'coding-oa-uikit/lib/icon/TeamOverview';
import Tiles from 'coding-oa-uikit/lib/icon/Tiles';
import Sitemap from 'coding-oa-uikit/lib/icon/Sitemap';
import LayoutMenu from '@src/component/layout-menu';
import { getApiDocURL } from '@plat/util';

const SideBar = () => {
  const { orgSid }: any = useParams();
  const { t } = useTranslation();

  return <LayoutMenu breakpoint="md" menus={[
    {
      icon: <Panel />,
      title: t('工作台'),
      link: `/t/${orgSid}/workspace`,
      key: 'workspace',
      regexMatch: /^\/t\/[^/]+\/workspace/i,
    },
    {
      icon: <Project />,
      title: t('项目'),
      link: `/t/${orgSid}/projects`,
      key: 'projects',
      regexMatch: /^\/t\/[^/]+\/projects/i,
    },
    {
      title: '',
      key: 'divider-1',
      divider: true,
    },
    {
      icon: <TeamOverview />,
      title: t('团队概览'),
      link: `/t/${orgSid}/profile`,
      key: 'profile',
      regexMatch: /^\/t\/[^/]+\/profile/i,
    },
    {
      icon: <Group />,
      title: t('团队成员'),
      link: `/t/${orgSid}/members`,
      key: 'members',
      regexMatch: /^\/t\/[^/]+\/members/i,
    },
    {
      title: '',
      key: 'divider-2',
      divider: true,
    },
    {
      icon: <Tiles />,
      title: t('工具管理'),
      link: `/t/${orgSid}/tools`,
      key: 'tools',
      regexMatch: /^\/t\/[^/]+\/tools/i,
      childrens: [
        {
          title: t('工具列表'),
          link: `/t/${orgSid}/tools`,
          key: 'checktools',
          regexMatch: /^\/t\/[^/]+\/tools/i,
        },
        {
          title: t('工具依赖'),
          link: `/t/${orgSid}/toollibs/`,
          key: 'toollibs',
          regexMatch: /^\/t\/[^/]+\/toollibs/i,
        },
      ],
    },
    {
      icon: <Sitemap />,
      title: t('节点管理'),
      link: `/t/${orgSid}/nodes/`,
      key: 'nodes',
    },
    {
      icon: <Api />,
      title: t('开放平台'),
      link: getApiDocURL(),
      key: 'docs',
      open: true,
    },
  ]} />;
};

export default SideBar;
