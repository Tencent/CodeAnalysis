import React, { useState, useEffect } from 'react';
import { t } from 'i18next';
import { Button, Row, Col, message } from 'coding-oa-uikit';
import Plus from 'coding-oa-uikit/lib/icon/Plus';

// 项目内
import { openWindow, PostMessageType, PostMessageCode } from '../../util/window';
import AuthTable from './auth-table';
import AuthModal from './auth-modal';
import { AuthTypeEnum } from './constant';
import { UserAuthAPI } from './types';

export * from './constant';
export * from './types';
export * from './api';

/** auth modal 初始值 */
const authConfInitData = {
  visible: false,
  authinfo: undefined,
};

/** UserAuth 入参数结构 */
interface UserAuthProps {
  /** auth 接口模块 */
  userAuthAPI: UserAuthAPI;
  /** 展示凭证创建渠道，默认false */
  showOrigin?: boolean;
}

const UserAuth = ({ userAuthAPI, showOrigin }: UserAuthProps) => {
  const [dataSource, setDataSource] = useState<any[]>([]);
  const [reload, setReload] = useState(false);
  const [authConf, setAuthConf] = useState(authConfInitData);

  useEffect(() => {
    // 获取凭证列表
    userAuthAPI.getAuths().then(setDataSource);
  }, [reload]);

  /**
   * 监听OAuth事件
   */
  useEffect(() => {
    const receiveOAuthHandler = (event: MessageEvent) => {
      const curLocation = window.location;
      if (event.origin === curLocation.origin) {
        if (event.data?.type === PostMessageType.GIT_OAUTH && event.data?.code === PostMessageCode.SUCCESS) {
          message.success(t('OAuth授权成功'));
          setReload(!reload);
        } else if (event.data?.type === PostMessageType.GIT_OAUTH && event.data?.code === PostMessageCode.FAIL) {
          message.error(t('OAuth授权失败'));
        }
      }
    };

    window.addEventListener('message', receiveOAuthHandler, false);
    return () => {
      window.removeEventListener('message', receiveOAuthHandler);
    };
  }, [reload]);

  /** 创建/更新凭证信息  */
  const onUpdateOrCreateHandler = (authinfo?: any) => {
    if (authinfo && authinfo.auth_type === AuthTypeEnum.OAUTH) {
      userAuthAPI.oauthStatus.get({ scm_platform_name: authinfo.scm_platform_name }).then((res: any) => {
        openWindow(res.git_auth_url || '', 'Git OAuth');
      })
        .catch(() => {
          message.error(t('平台暂未配置OAuth应用，无法去授权，请联系管理员。'));
        });
    } else {
      setAuthConf({
        visible: true,
        authinfo,
      });
    }
  };

  /** 删除当前凭证 */
  const onDeleteHandler = (authinfo: any) => {
    let promise = null;
    let msg = t('已删除凭证');
    switch (authinfo.auth_type) {
      case AuthTypeEnum.HTTP:
        promise = userAuthAPI.account.delete(authinfo.id);
        break;
      case AuthTypeEnum.SSH:
        promise = userAuthAPI.ssh.delete(authinfo.id);
        break;
      case AuthTypeEnum.OAUTH:
        msg = t('已取消授权');
        promise = userAuthAPI.oauthStatus.del({ scm_platform_name: authinfo.scm_platform_name });
        break;
    }
    promise?.then(() => {
      message.success(msg);
      setReload(!reload);
    });
  };

  return <><div style={{ marginBottom: 20 }}>
    <Row>
      <Col flex="auto">
        <h3 className="fs-18">{t('个人凭证管理')}</h3>
      </Col>
      <Col flex="200px" className="text-right">
        <Button
          type="primary"
          icon={<Plus />}
          onClick={() => onUpdateOrCreateHandler()}
        >
          {t('录入凭证')}
        </Button>
      </Col>
    </Row>
    <p className="text-grey-7">
      {t('录入后，仓库登记、分析项目等模块可直接选择凭证，无需重复填写。')}
    </p>
  </div>
    <AuthTable
      dataSource={dataSource}
      showOrigin={showOrigin}
      onEdit={onUpdateOrCreateHandler}
      onDel={onDeleteHandler}
    />
    <AuthModal
      visible={authConf.visible}
      authinfo={authConf.authinfo}
      userAuthAPI={userAuthAPI}
      onOk={() => {
        setAuthConf(authConfInitData);
        setReload(!reload);
      }}
      onCancel={() => {
        setAuthConf(authConfInitData);
      }}
    />
  </>;
};

export default UserAuth;
