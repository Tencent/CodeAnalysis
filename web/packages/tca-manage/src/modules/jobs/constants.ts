import { t } from '@src/i18n/i18next';

export const RUN_TYPE_ENUM = {
  TEMP: 0,
  DAILY: 2,
  APP: 5,
  CIBUILD: 6,
  LOCAL: 7,
};

export const RUN_TYPE_CHOICES = {
  [RUN_TYPE_ENUM.TEMP]: t('手动触发'),
  [RUN_TYPE_ENUM.DAILY]: t('定时触发'),
  [RUN_TYPE_ENUM.APP]: t('API接口触发'),
  [RUN_TYPE_ENUM.CIBUILD]: t('流水线触发'),
  [RUN_TYPE_ENUM.LOCAL]: t('本地客户端触发'),
};

export const RUN_TYPE_OPTIONS = [{
  text: RUN_TYPE_CHOICES[RUN_TYPE_ENUM.TEMP],
  value: RUN_TYPE_ENUM.TEMP,
}, {
  text: RUN_TYPE_CHOICES[RUN_TYPE_ENUM.DAILY],
  value: RUN_TYPE_ENUM.DAILY,
}, {
  text: RUN_TYPE_CHOICES[RUN_TYPE_ENUM.APP],
  value: RUN_TYPE_ENUM.APP,
}, {
  text: RUN_TYPE_CHOICES[RUN_TYPE_ENUM.CIBUILD],
  value: RUN_TYPE_ENUM.CIBUILD,
}, {
  text: RUN_TYPE_CHOICES[RUN_TYPE_ENUM.LOCAL],
  value: RUN_TYPE_ENUM.LOCAL,
}];

export const RESULT_ENUM = {
  SUCCESS: 0,
  EXCEPTION: 1,
  NULL: null,
};

export const RESULT_CHOICES = {
  [RESULT_ENUM.SUCCESS]: t('执行成功'),
  [RESULT_ENUM.EXCEPTION]: t('执行异常'),
};

export const RESULT_OPTIONS = [{
  label: RESULT_CHOICES[RESULT_ENUM.SUCCESS],
  value: RESULT_ENUM.SUCCESS,
}, {
  label: RESULT_CHOICES[RESULT_ENUM.EXCEPTION],
  value: RESULT_ENUM.EXCEPTION,
}];

export const STATE_ENUM = {
  WAITING: 0,
  RUNNING: 1,
  CLOSED: 2,
  CLOSING: 3,
  INITING: 4,
  INITED: 5,
};

export const STATE_CHOICES = {
  [STATE_ENUM.WAITING]: t('等待中'),
  [STATE_ENUM.RUNNING]: t('执行中'),
  [STATE_ENUM.CLOSED]: t('已结束'),
  [STATE_ENUM.CLOSING]: t('入库中'),
  [STATE_ENUM.INITING]: t('初始化'),
  [STATE_ENUM.INITED]: t('已初始化'),
};

export const STATE_OPTIONS = [
  {
    label: STATE_CHOICES[STATE_ENUM.INITING],
    value: STATE_ENUM.INITING,
  }, {
    label: STATE_CHOICES[STATE_ENUM.INITED],
    value: STATE_ENUM.INITED,
  }, {
    label: STATE_CHOICES[STATE_ENUM.WAITING],
    value: STATE_ENUM.WAITING,
  }, {
    label: STATE_CHOICES[STATE_ENUM.RUNNING],
    value: STATE_ENUM.RUNNING,
  }, {
    label: STATE_CHOICES[STATE_ENUM.CLOSING],
    value: STATE_ENUM.CLOSING,
  }, {
    label: STATE_CHOICES[STATE_ENUM.CLOSED],
    value: STATE_ENUM.CLOSED,
  }];
