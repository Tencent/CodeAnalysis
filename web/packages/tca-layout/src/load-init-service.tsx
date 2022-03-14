// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState, useEffect, FC } from 'react';
import { useDispatch } from 'react-redux';
import LoadingIcon from 'coding-oa-uikit/lib/icon/Loading';

// 项目内
import { t } from '@src/i18n/i18next';
import { useDispatchStore } from '@src/context/store';
import { SET_USERINFO } from '@src/context/constant';
import Constant from '@src/reducer/constant';
import { gUserInfo } from '@src/services/user';
import { setLayoutCompletedClass, info } from '@src/utils';

/**
 * 初始化页面时的一些请求
 */
const LoadInitService: FC = ({ children }: any) => {
  const [loading, setLoading] = useState<boolean>(true);
  const dispatch = useDispatchStore();
  const storeDispatch = useDispatch();

  useEffect(() => {
    storeDispatch({
      type: Constant.SET_LAYOUT_COMPLETED,
      payload: false,
    });
    // 获取用户信息，并存储到store中
    gUserInfo().then((res) => {
      dispatch({
        type: SET_USERINFO,
        payload: res,
      });
      setLoading(false);
      // layout加载完毕
      info('loading finished');
      storeDispatch({
        type: Constant.SET_USERINFO,
        payload: res
      })
      storeDispatch({
        type: Constant.SET_LAYOUT_COMPLETED,
        payload: true,
      });
    });
  }, []);

  setLayoutCompletedClass(loading);

  if (loading) {
    return (
      <div className="text-center pa-sm fs-12">
        <LoadingIcon />
        <span className="ml-xs">{t('正在加载')}...</span>
      </div>
    );
  }
  return <>{children}</>;
};

export default LoadInitService;
