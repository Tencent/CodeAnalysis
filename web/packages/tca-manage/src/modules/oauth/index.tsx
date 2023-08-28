/**
 * OAuth配置页面
 */
import React, { useState, useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { unionBy } from 'lodash';
import { MessagePlugin } from 'tdesign-react';

// 项目内
import { DeleteModal } from '@tencent/micro-frontend-shared/tdesign-component/modal';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { oauthSettingAPI } from '@src/services/oauth';
import { SCM_PLATFORM_CHOICES, ScmPlatformEnum, DEFAULT_SCM_PLATFORM } from '@plat/oauth';

// 模块内
import OAuthTable from './oauth-table';
import OAuthModal from './oauth-modal';
import { OAuthSettingData } from './types';

const OAuth = () => {
  const [listData, setListData] = useState<OAuthSettingData[]>([]);
  const [visibleEdit, setVisibleEdit] = useState<boolean>(false);
  const [visibleDel, setVisibleDel] = useState<boolean>(false);
  const [platformInfo, setPlatformInfo] = useState<OAuthSettingData>(null);
  const [reload, setReload] = useState<boolean>(false);
  const [create, setCreate] = useState<boolean>(false);


  useEffect(() => {
    /** 获取OAuth配置项列表 */
    oauthSettingAPI.get({ limit: 100 })
      .then(({ results = [] }: any) => {
        setListData(unionBy(results, DEFAULT_SCM_PLATFORM, 'scm_platform'));
      });
  }, [reload]);

  /**
   * 点击编辑凭证配置
   * @param platformInfo 凭证配置信息
   * @param create 是否创建操作
   */
  const onEditStart = (platformInfo: OAuthSettingData, create: boolean) => {
    setVisibleEdit(true);
    setPlatformInfo(platformInfo);
    setCreate(create);
  };

  /** 完成编辑操作，发起请求 */
  const onEditFinish = (platformInfo: OAuthSettingData, params: any) => {
    if (create) {
      // 初次创建配置
      oauthSettingAPI.create(params).then(() => {
        MessagePlugin.success(t('已创建配置'));
        setReload(!reload);
        onEditCancel();
      });
    } else {
      // 编辑已有配置
      oauthSettingAPI.delete(platformInfo.scm_platform_name).then(() => {
        oauthSettingAPI.create(params).then(() => {
          MessagePlugin.success(t('已更新配置'));
          setReload(!reload);
          onEditCancel();
        });
      });
    }
  };

  /** 点击编辑操作取消 */
  const onEditCancel = () => {
    setVisibleEdit(false);
  };

  /** 点击删除凭证配置 */
  const onDeleteStart = (platformInfo: OAuthSettingData) => {
    setPlatformInfo(platformInfo);
    setVisibleDel(true);
  };

  /**
   * 清除OAuth配置
   * @param platform_info 选中平台的配置信息
   */
  const onDeleteFinish = (platform_info: any) => {
    oauthSettingAPI.delete(platform_info.scm_platform_name).then(() => {
      MessagePlugin.success(t('已删除配置'));
      setReload(!reload);
      setVisibleDel(false);
    });
  };

  return (
    <>
      <PageHeader title="OAuth 管理" description="用于注册绑定第三方仓库平台，方便用户进行OAuth认证" />
      <div className="px-lg">
        <OAuthTable
          onDelete={onDeleteStart}
          onEdit={onEditStart}
          dataSource={listData}
        />
      </div>
      <OAuthModal
        visible={visibleEdit}
        scminfo={platformInfo}
        onCancel={onEditCancel}
        onOk={onEditFinish}
      />
      <DeleteModal
        actionType={t('删除')}
        objectType={t('OAuth配置')}
        confirmName={platformInfo && SCM_PLATFORM_CHOICES[platformInfo.scm_platform as ScmPlatformEnum]}
        visible={visibleDel}
        onCancel={() => setVisibleDel(false)}
        onOk={() => onDeleteFinish(platformInfo)}
      />
    </>
  );
};

export default OAuth;
