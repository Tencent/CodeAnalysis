// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import classnames from 'classnames';
import { get } from 'lodash';

// 项目内
import GlobalBreadcrumb from '@src/components/global-breadcrumb';
import { UPDATE_BREADCRUMB_DATA } from '@src/components/global-breadcrumb/types';

// 模块内
import s from './style.scss';
import RightZone from './right-zone';
import Enterprise from './enterprise';

const Header = () => {
  const { orgSid, name }: any = useParams();
  const storeDispatch = useDispatch();
  const APP = useSelector((state: any) => state.APP);
  const org = get(APP, 'org', {});

  const onBreadcrumbChange = (e: CustomEvent) => {
    const breadcrumbItems = e.detail;
    storeDispatch({
      type: UPDATE_BREADCRUMB_DATA,
      payload: breadcrumbItems,
    });
  };

  useEffect(() => {
    window.addEventListener('on-breadcrumb-change', onBreadcrumbChange);
    return window.removeEventListener('on-breadcrumb-change', onBreadcrumbChange);
  }, []);

  return (
    <header className={classnames(s.header)}>
      <div className={s.leftWrap}>
        <Enterprise org={org} orgSid={orgSid} teamName={name} />
      </div>
      <GlobalBreadcrumb />
      <div className={s.rightWrap}>
        <RightZone org={org.org_sid === orgSid ? org : {}} />
      </div>
    </header>
  );
};

export default Header;
