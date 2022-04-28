// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import { useParams } from 'react-router-dom';
import { t } from '@src/i18n/i18next';

import Panel from 'coding-oa-uikit/lib/icon/Panel';
import Group from 'coding-oa-uikit/lib/icon/Group';
import Project from 'coding-oa-uikit/lib/icon/Project';
import Api from 'coding-oa-uikit/lib/icon/Api';
import TeamOverview from 'coding-oa-uikit/lib/icon/TeamOverview';
import Tiles from 'coding-oa-uikit/lib/icon/Tiles';
import MenuLayout from '@src/components/menu-layout';
import { API_DOC_PATH } from '@src/utils/getRoutePath';

const SideBar = () => {
  const { orgSid }: any = useParams();

  const menus = [
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
      icon: <Api />,
      title: t('开放平台'),
      link: API_DOC_PATH,
      key: 'docs',
      open: true,
    },
  ];
  return <MenuLayout breakpoint="md" menus={menus} />;
};

export default SideBar;
