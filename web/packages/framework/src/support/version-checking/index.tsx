import React from 'react';
import ReactDOM from 'react-dom';
import { getMountedApps } from 'single-spa';
import { message } from 'tdesign-react';
import xorBy from 'lodash/xorBy';
import toInteger from 'lodash/toInteger';

import useInterval from '@src/utils/use-interval';
import { error, getMetaEnv, info, getOrCreateBodyContainer, isTrue } from '@src/utils';
import Constant, { DEFAULT_MICRO_FRONTEND_API, DEFAULT_MICRO_VERSION_INTERVAL } from '@src/constant';


// 微前端配置地址
const MICRO_FRONTEND_API = getMetaEnv(Constant.MICRO_FRONTEND_API, DEFAULT_MICRO_FRONTEND_API);

// 版本检查时间间隔
const MICRO_VERSION_INTERVAL = toInteger(getMetaEnv(Constant.MICRO_VERSION_INTERVAL)) || DEFAULT_MICRO_VERSION_INTERVAL;

// 系统级别是否开启版本检查
const MICRO_VERSION_ENABLED = isTrue(getMetaEnv(Constant.MICRO_VERSION_ENABLED, 'true'));

/**
 * 校验挂载的apps新旧版本
 * @param mountedApps
 */
const check = async (mountedApps: string[]) => {
  try {
    const res = await window.fetch(`${MICRO_FRONTEND_API}?time=${new Date().getTime()}`, { method: 'GET' });
    const latestConfig = await res.json();
    const loadedConfig = window.microHook.meta.map(config => config.props);
    const diff = xorBy(latestConfig, loadedConfig, 'commitId');
    // TODO: 只检查当前挂载的app，后续看看是存在配置更新就都更新，而不是仅检查当前挂载的app
    return diff.reduce((ret, d) => {
      if (mountedApps.includes(d.name)) {
        return [...ret, d];
      }
      return ret;
    }, []);
  } catch (e) {
    error('微前端版本更新失败');
    return [];
  }
};

const VersionChecking = () => {
  useInterval(() => {
    (async () => {
      // 获取当前挂载的apps
      const mountedApps = getMountedApps();
      const diffs = await check(mountedApps);
      if (diffs.length > 0) {
        message.info({
          content: <span
            style={{
              display: 'inline-block',
              verticalAlign: 'middle',
              marginLeft: '8px',
            }}
          >
            发现新版本，自动更新中...
          </span>,
          onClose: () => {
            window.location.reload();
          },
          icon: <img width="28px" height="28px" src="/static/images/favicon.ico" />,
        });
      }
    })();
  }, MICRO_VERSION_INTERVAL);

  return <></>;
};

if (MICRO_VERSION_ENABLED) {
  info('开启微前端版本检查');
  ReactDOM.render(<VersionChecking />, getOrCreateBodyContainer('version-checking'));
}
