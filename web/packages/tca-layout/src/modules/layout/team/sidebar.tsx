import React, { useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { t } from '@src/utils/i18n';

import Panel from 'coding-oa-uikit/lib/icon/Panel';
import Group from 'coding-oa-uikit/lib/icon/Group';
import Project from 'coding-oa-uikit/lib/icon/Project';
import Api from 'coding-oa-uikit/lib/icon/Api';
import TeamOverview from 'coding-oa-uikit/lib/icon/TeamOverview';
import Tiles from 'coding-oa-uikit/lib/icon/Tiles';
import Sitemap from 'coding-oa-uikit/lib/icon/Sitemap';
import Template from 'coding-oa-uikit/lib/icon/Template';
import LayoutMenu from '@src/component/layout-menu';
import { getApiDocURL } from '@plat/util';

const SideBar = () => {
  const { orgSid }: any = useParams();

  const menus = useMemo(() => [
    {
      icon: <Panel className='layoutMenuItemIcon' />,
      title: t('工作台'),
      link: `/t/${orgSid}/workspace`,
      key: 'workspace',
      regexMatch: /^\/t\/[^/]+\/workspace/i,
    },
    {
      icon: <Project className='layoutMenuItemIcon' />,
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
      icon: <TeamOverview className='layoutMenuItemIcon' />,
      title: t('团队概览'),
      link: `/t/${orgSid}/profile`,
      key: 'profile',
      regexMatch: /^\/t\/[^/]+\/profile/i,
    },
    {
      icon: <Group className='layoutMenuItemIcon' />,
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
      icon: <Tiles className='layoutMenuItemIcon' />,
      title: t('工具管理'),
      key: 'tools',
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
      icon: <Sitemap className='layoutMenuItemIcon' />,
      title: t('节点管理'),
      link: `/t/${orgSid}/nodes/`,
      key: 'nodes',
    },
    {
      icon: <Template className='layoutMenuItemIcon' />,
      title: t('分析方案模板'),
      link: `/t/${orgSid}/template`,
      key: 'template',
    },
    {
      icon: <Api className='layoutMenuItemIcon' />,
      title: t('开放平台'),
      link: getApiDocURL(),
      key: 'docs',
      open: true,
    },
  ], [orgSid]);

  return <LayoutMenu breakpoint="lg" menus={menus} />;
};

export default SideBar;
