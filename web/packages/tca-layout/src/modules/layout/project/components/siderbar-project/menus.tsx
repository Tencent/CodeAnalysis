import React from 'react';

// 项目内
import { t } from '@src/i18n/i18next';
import { MenuItem } from '@src/components/menu-layout';
import Repos from 'coding-oa-uikit/lib/icon/Repos';
import Scan from 'coding-oa-uikit/lib/icon/Scan';
import Template from 'coding-oa-uikit/lib/icon/Template';
import Api from 'coding-oa-uikit/lib/icon/Api';
import Group from 'coding-oa-uikit/lib/icon/Group';
import TeamOverview from 'coding-oa-uikit/lib/icon/TeamOverview';
import { API_DOC_PATH } from '@src/utils/getRoutePath';

const getTeamMenus = (orgSid: string, name: string): MenuItem[] => [
  {
    icon: <Repos />,
    title: t('仓库登记'),
    link: `/t/${orgSid}/p/${name}/repos`,
    key: 'repos',
    regexMatch: /^\/t\/[^/]+\/p\/[^/]+\/repos/i,
  },
  {
    icon: <Scan />,
    title: t('代码分析'),
    key: 'code-analysis',
    childrens: [
      {
        title: t('分支项目'),
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
    icon: <Template />,
    title: t('分析方案模板'),
    link: `/t/${orgSid}/p/${name}/template`,
    key: 'template',
    regexMatch: /^\/t\/[^/]+\/p\/[^/]+\/template/i,
  },
  {
    title: '',
    key: 'divider-1',
    divider: true,
  },
  {
    icon: <TeamOverview />,
    title: t('项目概览'),
    link: `/t/${orgSid}/p/${name}/profile`,
    key: 'profile',
    regexMatch: /^\/t\/[^/]+\/p\/[^/]+\/profile/i,
  },
  {
    icon: <Group />,
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
    icon: <Api />,
    title: t('开放平台'),
    link: API_DOC_PATH,
    key: 'docs',
    open: true,
  },
];

export default getTeamMenus;
