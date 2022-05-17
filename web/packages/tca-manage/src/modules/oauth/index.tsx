import React, { useState, useEffect } from 'react';
import { Row, Col, Tabs, Tag, message } from 'coding-oa-uikit';
import { unionBy, get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import DangerModal from '@src/components/modal/danger-modal';
import { getAllSettings, delOAuthSetting, postOAuthSetting } from '@src/services/oauth';

// 模块内
import s from './style.scss';
import { DEFAULT_SCM_PLATFORM, SCM_PLATFORM } from './constants';
import OAuthTable from './oauth-table';
import OAuthModal from './oauth-modal';

const { TabPane } = Tabs;

const downloadData = [
  {
    id: 1,
		client_id: '12313',
		client_secret : '13514365',
		redirect_uri : 'localhost',
		scm_platform : 6,
    scm_platform_name : "gitlab",
    scm_platform_desc : "由GitLab Inc.开发，一款基于Git的完全集成的软件开发平台",
	},
  {
    id: 2,
		client_id: '12313',
		client_secret : '13514365',
		redirect_uri : 'http://127.0.0.1/cb_git_auth/<str:scm_platform_name>/',
		scm_platform : 5,		
    scm_platform_name : "gitee",	
    scm_platform_desc : '开源中国于2013年推出的基于Git的代码托管和协作开发平台',
	},
];

const OAuth = () => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [visibleEdit, setVisibleEdit] = useState<boolean>(false);
  const [visibleDel, setVisibleDel] = useState<boolean>(false);
  const [platformInfo, setPlatformInfo] = useState<any>(null);
  const [reload, setReload] = useState<boolean>(false);

  /**
   * 根据路由参数获取团队列表
   */
  const getListData = () => {
    getAllSettings().then((response) => {
      console.log(response);
      setListData(unionBy(response,DEFAULT_SCM_PLATFORM,'scm_platform'));
    }).catch((e)=>{
      console.log(e);
      message.error('获取配置列表失败');
      setListData(unionBy(downloadData,DEFAULT_SCM_PLATFORM,'scm_platform'));
    });
    console.log('update data');
  };

  // 当路由参数变化时触发
  useEffect(() => {
    getListData();
  }, [reload]);

  const onEditStart = ( platform_info:any ) => {
    console.log('edit start');
    setVisibleEdit(true);
    setPlatformInfo(platform_info);
  };

  const onEditFinish = ( platform_info:any ) => {
    message.success('已更新配置');
    console.log(platform_info);
    setListData(unionBy([platform_info],listData,'scm_platform'));
    console.log(listData);
    postOAuthSetting(platformInfo).then((response) => {
      console.log(response);
      message.success('已更新配置');
      setReload(!reload);
    }).catch((e)=>{
      console.log(e);
      message.error('更新配置失败');
    }).finally(()=>{
      onEditCancel();
    });
  }

  const onEditCancel = () => {
    setVisibleEdit(false);
    setPlatformInfo(null);
  };


  const onDeleteStart = ( platform_info:any ) => {
    setPlatformInfo(platform_info);
    setVisibleDel(true);
  }

  const onDeleteFinish = ( platform_info:any ) => {
    message.success('已删除配置');
    console.log(platform_info?.scm_platform_name);
    delOAuthSetting(platform_info?.scm_platform_name).then((response) => {
      console.log(response);
      message.success('已删除配置');
      setReload(!reload);
    }).catch((e)=>{
      console.log(e);
      message.error('删除配置失败');
    }).finally(()=>{
      setVisibleDel(false);
    });
  }

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultActiveKey="apps" size="large">
            <TabPane tab={t('OAuth管理列表')} key="apps" />
          </Tabs>
        </Col>
      </Row>
      <div className="px-lg">
        <OAuthTable
        onDelete={onDeleteStart}
        onEdit={onEditStart}
        dataSource={listData}
        />
        <OAuthModal
        visible={visibleEdit}
        scminfo={platformInfo}
        onCancel={onEditCancel}
        onOk={onEditFinish}
        />
        <DangerModal
        title={t('删除配置')}
        visible={visibleDel}
        onCancel={() => setVisibleDel(false)}
        onOk={() => onDeleteFinish(platformInfo)}
        content={
          <div>
            {t('确认删除 ')}
            <Tag color="default">{get(SCM_PLATFORM, platformInfo?.scm_platform) || 'unknown'}</Tag>
            {t('的OAuth应用配置？')}
          </div>
        }
        />
      </div>
    </>
  );
};

export default OAuth;
