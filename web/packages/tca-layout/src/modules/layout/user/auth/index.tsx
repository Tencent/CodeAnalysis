import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { filter, get, isEmpty } from 'lodash';
import { Layout, Button, Row, Col, Tag, message } from 'coding-oa-uikit';
import { DangerModal } from '@tencent/micro-frontend-shared/component/modal';
import { openWindow, PostMessageType, PostMessageCode } from '@tencent/micro-frontend-shared/util/window';
import Plus from 'coding-oa-uikit/lib/icon/Plus';

// 项目内
import { AuthTypeEnum, DEFAULT_SCM_PLATFORM } from '@src/constant';
import { UserAPI } from '@plat/api';
import AuthModal from './auth-modal';
import AuthTable from './auth-table';
import s from '../style.scss';

const { Content } = Layout;


interface AuthProps {
  /** 展示凭证所属平台，默认true */
  showPlatform?: boolean;
  /** 展示凭证创建渠道，默认false */
  showOrigin?: boolean;
}

const Auth = ({ showPlatform = true, showOrigin = false }: AuthProps) => {
  const [dataSource, setDataSource] = useState<any>([]);
  const [visible, setVisible] = useState(false);
  const [visibleDel, setVisibleDel] = useState(false);
  const [curAuthInfo, setCurAuthInfo] = useState<any>({});
  const [authinfo, setAuthinfo] = useState(null);
  const [reload, setReload] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    const all: Promise<any>[] = [
      UserAPI.authSSH().get({ limit: 200 })
        .then(({ results }: RestfulListAPIParams) => results || []),
      UserAPI.authAccount().get({ limit: 200 })
        .then(({ results }: RestfulListAPIParams) => results || []),
      UserAPI.getPlatformStatus().then(r => r || {}),
      UserAPI.getOAuthStatus().then(r => r || {}),
    ];
    /** 获取全部凭证 */
    Promise.all(all).then((result) => {
      let res = [
        ...(result[0] || []).map((item: any) => ({ ...item, auth_type: AuthTypeEnum.SSH })),
        ...(result[1] || []).map((item: any) => ({ ...item, auth_type: AuthTypeEnum.HTTP })),
      ];
      const oauthInfo: any = filter(
        DEFAULT_SCM_PLATFORM.map((item: any) => ({
          ...item,
          oauth_status: get(result[3], item.scm_platform_name, [false]),
          platform_status: get(result[2], item.scm_platform_name, [false]),
          auth_type: AuthTypeEnum.OAUTH,
        })),
        'platform_status',
      );
      if (!isEmpty(oauthInfo)) {
        res = oauthInfo.concat(res);
      }
      setDataSource(res);
    });
  }, [reload]);

  /**
   * 监听OAuth事件
   */
  useEffect(() => {
    window.addEventListener('message', receiveOAuthStatus, false);
    return () => {
      window.removeEventListener('message', receiveOAuthStatus);
    };
  }, []);

  /**
   * 接收OAuth授权结果
   */
  const receiveOAuthStatus = (event: MessageEvent) => {
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

  /** 创建/更新凭证信息  */
  const onCreateOrEditHandler = (authinfo: any = null) => {
    if (authinfo && authinfo.auth_type === AuthTypeEnum.OAUTH) {
      UserAPI.getOAuthStatus({ scm_platform_name: authinfo?.scm_platform_name }).then((res: any) => {
        openWindow(res?.git_auth_url || '', 'Git OAuth');
      })
        .catch(() => {
          message.error(t('平台暂未配置OAuth应用，无法去授权，请联系管理员。'));
        });
    } else {
      setAuthinfo(authinfo);
      setVisible(true);
    }
  };

  /** 删除当前凭证 */
  const onDelAuthHandler = (curAuthInfo: any) => {
    let promise = null;
    switch (curAuthInfo.auth_type) {
      case AuthTypeEnum.HTTP:
        promise = UserAPI.authAccount().delete(curAuthInfo.id);
        break;
      case AuthTypeEnum.SSH:
        promise = UserAPI.authSSH().delete(curAuthInfo.id);
        break;
      case AuthTypeEnum.OAUTH:
        promise = UserAPI.delOAuthStatus({ scm_platform_name: curAuthInfo?.scm_platform_name });
        break;
    }
    promise.then(() => {
      message.success(t('已删除凭证'));
      setVisibleDel(false);
      setReload(!reload);
    });
  };

  return (
    <Content className="pa-lg">
      <div className={s.header}>
        <Row>
          <Col flex="auto">
            <h3 className="fs-18">{t('凭证管理')}</h3>
          </Col>
          <Col flex="200px" className=" text-right">
            <Button
              type="primary"
              icon={<Plus />}
              onClick={() => onCreateOrEditHandler()}
            >
              {t('录入凭证')}
            </Button>
          </Col>
        </Row>
        <p className="text-grey-7">
          {t('录入后，仓库登记、分支项目等模块可直接选择凭证，无需重复填写。')}
        </p>
      </div>
      <AuthTable
        dataSource={dataSource}
        showPlatform={showPlatform}
        showOrigin={showOrigin}
        onEdit={onCreateOrEditHandler}
        onDel={(authinfo) => {
          setCurAuthInfo(authinfo);
          setVisibleDel(true);
        }}
      />
      <AuthModal
        visible={visible}
        authinfo={authinfo}
        onOk={() => {
          setVisible(false);
          setReload(!reload);
        }}
        onCancel={() => setVisible(false)}
      />
      <DangerModal
        title={t('删除凭证')}
        visible={visibleDel}
        onCancel={() => setVisibleDel(false)}
        onOk={() => onDelAuthHandler(curAuthInfo)}
        content={
          <div>
            {t('确认删除凭证')}{' '}
            <Tag color='red'>
              {curAuthInfo.scm_username || curAuthInfo.name || 'OAuth'}
            </Tag>{' '}
            {t('？')}
          </div>
        }
      />
    </Content>
  );
};

export default Auth;
