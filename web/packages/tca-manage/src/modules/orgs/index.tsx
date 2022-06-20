import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { Row, Col, Tabs, Modal, message } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { getPaginationParams, getFilterURLPath } from '@src/utils';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useURLParams, useDeepEffect } from '@src/utils/hooks';
import { getOrgs, putOrgStatus } from '@src/services/orgs';
import DeleteModal from '@src/components/delete-modal';

// 模块内
import s from './style.scss';
import Search from './search';
import OrgTable from './org-table';
import { ORG_STATUS_ENUM } from './constants';

const { TabPane } = Tabs;
const { confirm } = Modal;

const FILTER_FIELDS = ['name', 'status'];

const customFilterURLPath = (params = {}) => getFilterURLPath(FILTER_FIELDS, params);

const Orgs = () => {
  const history = useHistory();
  const [listData, setListData] = useState<Array<any>>([]);
  const [count, setCount] = useState<number>(DEFAULT_PAGER.count);
  const [loading, setLoading] = useState<boolean>(false);
  const [reload, setReload] = useState<boolean>(false);
  const { filter, currentPage, searchParams } = useURLParams(FILTER_FIELDS);
  const [deleteVisible, setDeleteVisible] = useState<boolean>(false);
  const [curOrg, setCurOrg] = useState<any>(null);

  /**
     * 根据路由参数获取团队列表
     */
  const getListData = () => {
    setLoading(true);
    getOrgs(filter).then((response) => {
      setCount(response.count);
      setListData(response.results || []);
      setLoading(false);
    });
  };

  // 当路由参数变化时触发
  useDeepEffect(() => {
    getListData();
  }, [filter]);

  // 手动触发
  useEffect(() => {
    getListData();
  }, [reload]);

  // 筛选
  const onSearch = (params: any) => {
    history.push(customFilterURLPath({
      limit: DEFAULT_PAGER.pageSize,
      offset: DEFAULT_PAGER.pageStart,
      ...params,
    }));
  };

  // 翻页
  const onChangePageSize = (page: number, pageSize: number) => {
    const params = getPaginationParams(page, pageSize);
    history.push(customFilterURLPath(params));
  };

  // 禁用团队
  const onDeleteOrg = (org: any) => {
    setDeleteVisible(true);
    setCurOrg(org);
  };

  const handleDeleteOrg = () => {
    putOrgStatus(curOrg.org_sid, {status: ORG_STATUS_ENUM.INACTIVE}).then(() => {
      message.success(t('已禁用团队'));
      setReload(!reload);
      setDeleteVisible(false);
      setCurOrg(null);
    });
  };

  // 恢复团队
  const onRecoverOrg = (org: any) => {
    confirm({
      title: t('恢复团队'),
      content: t('确定要恢复已禁用的团队吗？'),
      onOk() {
        putOrgStatus(org.org_sid, {status: ORG_STATUS_ENUM.ACTIVE}).then(() => {
          message.success(t('已恢复团队'));
          setReload(!reload);
        });
      },
      onCancel() {},
    });
  };

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultActiveKey="project" size="large">
            <TabPane tab={t('团队列表')} key="project" />
          </Tabs>
        </Col>
      </Row>
      <div className={s.filterContent}>
        <Search loading={loading} searchParams={searchParams} callback={onSearch} />
      </div>
      <div className="px-lg">
        <OrgTable
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
            onChange: onChangePageSize,
          }}
          onDelete={onDeleteOrg}
          onRecover={onRecoverOrg}
        />
      </div>
      <DeleteModal
        actionType={t('禁用')}
        objectType={t('团队')}
        confirmName={curOrg?.name}
        visible={deleteVisible}
        onCancel={() => setDeleteVisible(false)}
        onOk={handleDeleteOrg}
      />
    </>
  );
};

export default Orgs;
