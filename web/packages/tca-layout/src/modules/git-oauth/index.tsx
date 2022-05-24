// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 所有团队
 */

import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import { getQuery } from '@src/utils';
import { useParams } from 'react-router-dom';
 
import { Spin, message, Layout } from 'coding-oa-uikit';
//  import { t } from '@src/i18n/i18next';

import { getOAuthCallBack } from '@src/services/user';
 
const { Content } = Layout;
 
const GitOAuth = () => {
  const containerNode = document.getElementById('container');
  const query = getQuery();
  const { scm_platform_name }: any = useParams();

  useEffect(() => {
    const opener = window.opener;
    getOAuthCallBack(scm_platform_name,query).then(()=>{
      message.success('授权成功');
      opener.postMessage('oauth succeeded',opener.location.origin);
    }).catch(()=>{
      message.error('授权失败');
      opener.postMessage('oauth failed',opener.location.origin);
    }).finally(()=>{
      window.close();
    });
  }, []);

  return (
    <>
      {containerNode
        && ReactDOM.createPortal(
          <Content className="pa-lg" style={{textAlign:'center'}}>
            <Spin 
            size='large' 
            tip='OAuth授权中'
            />
          </Content>,
          containerNode,
        )}
    </>
  );
};

export default GitOAuth;
 