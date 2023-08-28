/**
 * 工具依赖
 */

import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button, Space } from 'tdesign-react';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';

import { getToolLibs } from '@src/services/tools';

import { TOOLLIB_FILTER_FIELDS as filterFields, TOOLLIB_SEARCH_FIELDS } from './constants';
import CreateToollibs from './create-libs';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { t } from '@src/utils/i18n';

import Table from './lib-table';
import { useOrgAdminPerm } from '@src/utils/hooks';

export const ToolLibs = () => {
  const { orgSid }: any = useParams();
  // 弹框
  const [modalData, setModalData] = useState({
    visible: false,
    libId: null,
  });
  // 是否可编辑
  const [editable, , isSuperuser] = useOrgAdminPerm();
  // 数据源
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }, reload] = useFetch(getToolLibs, [orgSid, filter]);
  const { results: listData = [], count = 0 } = data || {};

  return (
    <>
      <PageHeader title={t('工具依赖')} description={t('工具最小单元，用于组合工具')} action={
        editable && (
          <Button
            theme='primary'
            onClick={() => setModalData({
              visible: true,
              libId: null,
            })}
          >
            {t('添加依赖')}
          </Button>
        )
      } />
      <Search
        searchParams={searchParams}
        fields={TOOLLIB_SEARCH_FIELDS}
      />
      <div className='tca-px-lg'>
        <Table loading={isLoading} dataSource={listData}
          opCell={row => <Space>
            <Button variant='text' theme='primary' onClick={() => setModalData({ visible: true, libId: row.id })} >{t('编辑')}</Button>
          </Space>}
          pagination={{
            current: currentPage,
            total: count,
            pageSize,
          }} />
      </div>
      {
        editable && (
          <CreateToollibs
            orgSid={orgSid}
            isSuperuser={isSuperuser}
            visible={modalData.visible}
            libId={modalData.libId}
            onClose={() => setModalData({
              visible: false,
              libId: null,
            })}
            callback={() => reload()}
          />
        )
      }
    </>
  );
};

export default ToolLibs;
