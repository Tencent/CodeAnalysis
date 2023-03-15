import React, { useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { Tabs } from 'tdesign-react';

// 项目内
import { clearLoginLocalStorage } from '@src/utils';
import s from '@src/style.scss';
import { LoginTypeEnum } from '@plat/constant';
import NormalSignin from './signin';
import Language from './language';

const { TabPanel } = Tabs;

const Login = () => {
  useEffect(() => {
    // 每次进来都清除storage
    clearLoginLocalStorage();
  }, []);

  return (
    <div className={s.login}>
      <div className={s.content}>
        <Tabs className={s.body} defaultValue={LoginTypeEnum.NORMAL_SIGNIN} size="large">
          <TabPanel label={t('腾讯云代码分析账号密码登录')} value={LoginTypeEnum.NORMAL_SIGNIN}>
            <NormalSignin />
          </TabPanel>
        </Tabs>
      </div>
      <Language />
    </div>
  );
};

export default Login;
