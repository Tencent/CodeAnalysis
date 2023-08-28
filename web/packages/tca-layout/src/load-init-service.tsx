import React, { useState, useEffect, FC } from 'react';
import { useDispatch } from 'react-redux';
import { useDispatchStore } from '@tencent/micro-frontend-shared/hook-store';
import { useFetch } from '@tencent/micro-frontend-shared/hooks';
import { LogMgr } from '@tencent/micro-frontend-shared/util';
import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';

// 项目内
import Constant from '@src/reducer/constant';
import { UserAction, SET_USERINFO } from '@src/store/user';
import { getUserAvatarURL } from '@src/utils';
import { UserAPI } from '@plat/api';
import { initRequest, reportUserInfo } from '@plat/util';
import { useNotification, useVersionChangeRedirect } from '@plat/hooks';

/**
 * 初始化页面时的一些请求
 */
const LoadInitService: FC = ({ children }: any) => {
  const [loading, setLoading] = useState<boolean>(true);
  const dispatch = useDispatchStore<UserAction>();
  const storeDispatch = useDispatch();

  useNotification();
  useVersionChangeRedirect();

  useEffect(() => {
    // 处理一些初始化时额外需要的请求
    initRequest?.(dispatch, storeDispatch);
  }, [dispatch, storeDispatch]);

  useFetch(UserAPI.getUserInfo, [], {
    onPreHandler: () => {
      storeDispatch({
        type: Constant.SET_LAYOUT_COMPLETED,
        payload: false,
      });
    },
    onSuccess: (data) => {
      const { avatar, avatar_url: avatarUrl } = data;
      const url = avatar || avatarUrl || getUserAvatarURL(data);
      const userinfo = {
        ...data,
        avatar: url,
        avatar_url: url,
      };
      dispatch({
        type: SET_USERINFO,
        payload: userinfo,
      });
      storeDispatch({
        type: Constant.SET_USERINFO,
        payload: userinfo,
      });
      setLoading(false);
      // layout加载完毕
      LogMgr.info('loading finished');
      const timer = setTimeout(() => {
        storeDispatch({
          type: Constant.SET_LAYOUT_COMPLETED,
          payload: true,
        });
        clearTimeout(timer);
      }, 200);
      reportUserInfo(userinfo);
    },
  });

  useEffect(() => {
    // 根据loading状态设置layout加载class，用于控制container显示/隐藏
    const node = document.getElementById('main-container');
    const layoutUnCompletedClass = 'layout-uncompleted';
    if (node) {
      if (loading && !node.classList.contains(layoutUnCompletedClass)) {
        node.classList.add(layoutUnCompletedClass);
      } else if (!loading && node.classList.contains(layoutUnCompletedClass)) {
        node.classList.remove(layoutUnCompletedClass);
      }
    }
  }, [loading]);

  if (loading) {
    return <Loading />;
  }
  return <>{children}</>;
};

export default LoadInitService;
