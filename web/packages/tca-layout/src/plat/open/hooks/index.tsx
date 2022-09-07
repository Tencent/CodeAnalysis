import React from 'react';
import { useNotification as useNotify } from '@tencent/micro-frontend-shared/component/notification';
import { NotificationProps } from '@tencent/micro-frontend-shared/component/notification/useNotification';
export * from '@src/plat/common/hooks';

const licenseTrialNotify: NotificationProps = {
  key: 'notify-license-trial',
  type: 'info',
  useExpireOper: true,
  notifyArgs: {
    message: '免费体验增强分析模块',
    description: <>
      TCA为开源社区免费提供更多功能精度更高的增强分析模块，欢迎免费申请License体验。详情请参考<a className='text-weight-medium' href="https://tencent.github.io/CodeAnalysis/zh/quickStarted/enhanceDeploy.html" target='_blank' rel="noreferrer" >增强分析模块文档</a>
    </>,
  },
};

export const useNotification = () => {
  useNotify(licenseTrialNotify);
};
