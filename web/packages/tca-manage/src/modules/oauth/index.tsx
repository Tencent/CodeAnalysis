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

const OAuth = () => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [visibleEdit, setVisibleEdit] = useState<boolean>(false);
  const [visibleDel, setVisibleDel] = useState<boolean>(false);
  const [platformInfo, setPlatformInfo] = useState<any>(null);
  const [reload, setReload] = useState<boolean>(false);
  const [create, setCreate] = useState<boolean>(false);

  /**
   * 获取OAuth平台列表
   */
  const getListData = () => {
    getAllSettings().then((response) => {
      console.log(response.results);
      setListData(unionBy(response.results,DEFAULT_SCM_PLATFORM,'scm_platform'));
    }).catch((e)=>{
      console.log(e);
      message.error('获取配置列表失败');
    });
    console.log('update data');
  };


  useEffect(() => {
    getListData();
  }, [reload]);

  /**
   * 编辑OAuth配置
   * @param platform_info 选中平台的配置信息
   */
  const onEditStart = ( platform_info:any, create:boolean ) => {
    console.log('edit start');
    setVisibleEdit(true);
    setPlatformInfo(platform_info);
    setCreate(create);
  };

  /**
   * 上传OAuth配置
   * @param platform_info 表单内容
   */
  const onEditFinish = ( platform_info:any ) => {

    if (create) {
      //初次创建配置
      postOAuthSetting(platform_info).then(() => {
        message.success('已创建配置');
        setReload(!reload);
      }).catch(()=>{
        message.error('创建配置失败');
      }).finally(()=>{
        onEditCancel();
      });
    } else {
      //编辑已有配置
      delOAuthSetting(platformInfo?.scm_platform_name).then(() => {
        postOAuthSetting(platform_info).then(() => {
          message.success('已更新配置');
          setReload(!reload);
        });
      }).catch(()=>{
        message.error('更新配置失败');
      }).finally(()=>{
        onEditCancel();
      });
    }

  }

  const onEditCancel = () => {
    setVisibleEdit(false);
    setPlatformInfo(null);
  };

  const onDeleteStart = ( platform_info:any ) => {
    setPlatformInfo(platform_info);
    setVisibleDel(true);
  }

  /**
   * 清除OAuth配置
   * @param platform_info 选中平台的配置信息
   */
  const onDeleteFinish = ( platform_info:any ) => {
    delOAuthSetting(platform_info?.scm_platform_name).then(() => {
      message.success('已删除配置');
      setReload(!reload);
    }).catch(()=>{
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
            <TabPane tab={t('OAuth配置列表')} key="apps" />
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
