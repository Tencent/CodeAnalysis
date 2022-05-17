import React, { useState, useEffect } from 'react';
import { Row, Col, Tabs } from 'coding-oa-uikit';
import { concat } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';

// 模块内
import s from './style.scss';

import OAuthTable from './oauth-table';
import OAuthModal from './oauth-modal';

const { TabPane } = Tabs;

const oauthData = [
  {
    id: 1,
		client_id: '12313',
		client_secret : '13514365',
		redirect_uri : 'http://<部署机IP>/cb_git_auth/<str:scm_platform_name>/',
		scm_platform : 2,			
		scm_platform_name : "github",
		scm_platform_desc : '12313',
	},
  {
    id: 2,
		client_id: '12313',
		client_secret : '13514365',
		redirect_uri : 'http://<部署机IP>/cb_git_auth/<str:scm_platform_name>/',
		scm_platform : 3,			
		scm_platform_name : "github",
		scm_platform_desc : '12313',
	},
  {
    id: 3,
		scm_platform : 4,	
	},
  {
    id: 4,
		scm_platform : 5,			
	},
  {
    id: 5,
		scm_platform : 6,			
	},
];

const OAuth = () => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [visible, setVisible] = useState(false);
  const [platformInfo, setPlatformInfo] = useState(null);

  /**
   * 根据路由参数获取团队列表
   */
  const getListData = () => {
    setListData(oauthData);
  };

  // 当路由参数变化时触发
  useEffect(() => {
    getListData();
  }, []);

  const onCreateOrUpdateHandle = ( platform_info:any ) => {
    setVisible(true);
    setPlatformInfo(platform_info);
  };

  const onCancel = () => {
    setVisible(false);
    setPlatformInfo(null);
  };

  const onEdit = ( platform_info:any ) => {
    onCreateOrUpdateHandle(platform_info);
    console.log('edit');
    console.log(platform_info);
  }

  const onDelete = ( platform_info:any ) => {
    console.log('delete');
    console.log(platform_info);
  }

  const onEditFinish = ( platform_info:any ) => {
    console.log(concat(oauthData,platform_info));
    setListData(concat(oauthData,platform_info));
    onCancel();
  }

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultActiveKey="apps" size="large">
            <TabPane tab={t('OAuth管理列表')} key="apps" />
          </Tabs>
        </Col>
        {/* <Col flex="none">
          <Button type="primary" onClick={onCreateOrUpdateHandle}>
            {t('登记OAuth应用')}
          </Button>
        </Col> */}
      </Row>
      <div className="px-lg">
        <OAuthTable
        onDelete={onDelete}
        onEdit={onEdit}
        dataSource={listData}
        />
        <OAuthModal
        visible={visible}
        scminfo={platformInfo}
        onCancel={onCancel}
        onOk={onEditFinish}
        />
      </div>
    </>
  );
};

export default OAuth;
