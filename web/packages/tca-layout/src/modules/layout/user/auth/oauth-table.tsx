// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import { Table, Button, Tag } from 'coding-oa-uikit';
import Refresh from 'coding-oa-uikit/lib/icon/Refresh';
import Stop from 'coding-oa-uikit/lib/icon/Stop';
import Link from 'coding-oa-uikit/lib/icon/Link';
import { get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import { SCM_PLATFORM } from '@src/utils/constant';
import s from '../style.scss';

interface IProps {
  dataSource: Array<any>;
  onOAuth?: (oauthinfo: any) => void;
  onUpdate?: (oauthinfo: any) => void;
  onDel?: (oauthinfo: any) => void;
}
const OAuthTable = (props: IProps) => {
  const { dataSource, onOAuth, onUpdate, onDel } = props;

  const columns = [
    {
      title: t('平台'),
      dataIndex: 'scm_platform',
      key: 'scm_platform',
      width: 200,
      render: (scm_platform: string) => (
        <span>{get(SCM_PLATFORM, scm_platform) || scm_platform}</span>
      ),
    },
    {
      title: t('OAuth状态'),
      dataIndex: 'oauth_status',
      key: 'oauth_status',
      width: 200,
      render: (oauth_status: boolean) => (
        oauth_status === true ? <Tag color='success'>已认证</Tag> : <Tag color='default'>未认证</Tag>
      ),
    },
    {
      title: t('操作'),
      dataIndex: 'oauth_status',
      key: 'op',
      width: 200,
      render: (oauth_status: boolean, oauth_info:any) => (
        oauth_status === true ? <>
        <Button type="text" icon={<Refresh/>} onClick={()=>onUpdate(oauth_info)}/>
        <Button type="text" icon={<Stop />} onClick={()=>onDel(oauth_info)}/>
        </> : <>
        <Button type="text" icon={<Link />} onClick={()=>onOAuth(oauth_info)}/>
        </>
      ),
    },
  ];
  return (
    <Table
      pagination={false}
      rowKey={(item: any) => item.scm_platform }
      dataSource={dataSource}
      columns={columns}
      className={s.oauthTable}
    />
  );
};

export default OAuthTable;
