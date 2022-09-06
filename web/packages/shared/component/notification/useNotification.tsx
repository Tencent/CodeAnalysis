import React, { useEffect } from 'react';
import Moment from 'moment';
import { notification, Button, Space } from 'coding-oa-uikit';
import { ArgsProps } from 'coding-oa-uikit/lib/notification';

/** 通知存储数据结构 */
interface NotifyStorageData {
  /** 不再提醒 */
  neverRemind: boolean;
  /** 过期时间 */
  expireTimestamp?: number;
}

/** 获取在LocalStorage的通知数据 */
const getNotificationDataByLocalStorage = (key: string) => {
  const keyValue = localStorage.getItem(key);
  if (keyValue) {
    try {
      const keyObj: NotifyStorageData = JSON.parse(keyValue);
      return keyObj;
    } catch (error) {
      // 解析失败
    }
  }
  return null;
};

/** 设置通知数据到LocalStorage */
const setNotificationDataToLocalStorage = (key: string, notifyStorageData: NotifyStorageData) => {
  localStorage.setItem(key, JSON.stringify(notifyStorageData));
};

/** 通知入参数数据结构 */
export interface NotificationProps {
  /** 唯一标识 */
  key: string,
  /** 通知类型 */
  type: 'info' | 'success' | 'error' | 'warning',
  /** 是否开启过期操作 */
  useExpireOper?: boolean;
  /** 通知其他参数 */
  notifyArgs: Omit<ArgsProps, 'key'>
}

/** 通知hooks */
const useNotification = ({ key, type, useExpireOper = false, notifyArgs }: NotificationProps) => {
  const { btn, ...rest } = notifyArgs;

  useEffect(() => {
    if (useExpireOper) {
      const notifyStorageData = getNotificationDataByLocalStorage(key);
      if (notifyStorageData?.neverRemind
        || (notifyStorageData?.expireTimestamp && Moment().valueOf() < notifyStorageData.expireTimestamp)
      ) {
        return;
      }
    }

    notification[type]({
      duration: null,
      btn: useExpireOper ? <Space>
        <Button type="primary" size="small" onClick={() => {
          // 明日凌点时间戳
          const timestamp = Moment().startOf('day')
            .add(1, 'day')
            .valueOf();
          const notifyStorageData: NotifyStorageData = {
            neverRemind: false,
            expireTimestamp: timestamp,
          };
          setNotificationDataToLocalStorage(key, notifyStorageData);
          notification.close(key);
        }}>
          今日不再提醒
        </Button>
        <Button type="secondary" size="small" onClick={() => {
          const notifyStorageData: NotifyStorageData = { neverRemind: true };
          setNotificationDataToLocalStorage(key, notifyStorageData);
          notification.close(key);
        }}>
          不再提醒
        </Button>
      </Space> : btn,
      ...rest,
      key,
    });
  }, []);
};

export default useNotification;
