import React, { useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { Tabs, Card, Space } from 'tdesign-react';
import { LockOnIcon } from 'tdesign-icons-react';

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
        <Card className={s.body} shadow bordered={false} footer={<Language />}>
          <Tabs defaultValue={LoginTypeEnum.NORMAL_SIGNIN} >
            <TabPanel label={
              <Space size={2} ><LockOnIcon size={20} style={{ marginBottom: 2 }} /> {t('账号登录')}</Space>
            } value={LoginTypeEnum.NORMAL_SIGNIN}>
              <NormalSignin />
            </TabPanel>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

export default Login;
