import React, { useState, useEffect } from 'react';
import { Row, Col, Tabs, Tag } from 'coding-oa-uikit';
import { unionBy, get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import DangerModal from '@src/components/modal/danger-modal';

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
  const [visibleEdit, setVisibleEdit] = useState(false);
  const [visibleDel, setVisibleDel] = useState(false);
  const [platformInfo, setPlatformInfo] = useState(null);

  /**
   * 根据路由参数获取团队列表
   */
  const getListData = () => {
    setListData(unionBy(downloadData,DEFAULT_SCM_PLATFORM,'scm_platform'));
  };

  // 当路由参数变化时触发
  useEffect(() => {
    getListData();
  }, []);

  const onEditStart = ( platform_info:any ) => {
    console.log('edit start');
    setVisibleEdit(true);
    setPlatformInfo(platform_info);
  };

  const onEditFinish = ( platform_info:any ) => {
    console.log(platform_info);
    // setListData(unionBy([platform_info],listData,'scm_platform'));
    // console.log(listData);
    onEditCancel();
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
    console.log('yes delete');
    console.log(platform_info?.scm_platform_name);
    setVisibleDel(false);
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
