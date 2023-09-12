import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { DialogPlugin, MessagePlugin } from 'tdesign-react';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { getOrgs, putOrgStatus } from '@src/services/orgs';
import { DeleteModal } from '@tencent/micro-frontend-shared/tdesign-component/modal';

// 模块内
import { ORG_FILTER_FIELDS as filterFields, ORG_SEARCH_FIELDS, OrgStatusEnum } from './constants';
import OrgTable from './org-table';

const Orgs = () => {
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }, reload] = useFetch(getOrgs, [filter]);
  const { results: listData = [], count = 0 } = data || {};
  const [deleteVisible, setDeleteVisible] = useState<boolean>(false);
  const [curOrg, setCurOrg] = useState<any>(null);

  // 禁用团队
  const onDeleteOrg = (org: any) => {
    setDeleteVisible(true);
    setCurOrg(org);
  };

  /** 删除团队操作 */
  const handleDeleteOrg = () => {
    putOrgStatus(curOrg.org_sid, { status: OrgStatusEnum.INACTIVE }).then(() => {
      MessagePlugin.success(t('已禁用团队'));
      reload();
      setDeleteVisible(false);
      setCurOrg(null);
    });
  };

  // 恢复团队
  const onRecoverOrg = (org: any) => {
    const confirmDia = DialogPlugin.confirm({
      header: t('恢复团队'),
      body: t('确定要恢复已禁用的团队吗？'),
      onConfirm() {
        putOrgStatus(org.org_sid, { status: OrgStatusEnum.ACTIVE }).then(() => {
          MessagePlugin.success(t('已恢复团队'));
          confirmDia.hide();
          reload();
        });
      },
      onClose() {
        confirmDia.hide();
      },
    });
  };


  return (
    <>
      <PageHeader title={t('团队列表')} description="平台注册登录的团队列表" />
      <Search fields={ORG_SEARCH_FIELDS} loading={false} searchParams={searchParams} />
      <div className="px-lg">
        <OrgTable
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            pageSize,
          }}
          loading={isLoading}
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
