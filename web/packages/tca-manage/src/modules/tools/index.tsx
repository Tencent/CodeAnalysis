/**
 * 工具管理功能
 * biz-start
 * 目前适用于体验、开源
 * biz-end
 */
import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { Row, Col, Tabs } from 'tdesign-react';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { getTools } from '@src/services/tools';

// 模块内
import { TOOL_FILTER_FIELDS as filterFields, TOOL_SEARCH_FIELDS } from './constants';
import ToolTable from './tool-table';
import ToolPermModal from './tool-perm-modal';
import { ToolData } from './types';
import s from '../style.scss';

const { TabPanel } = Tabs;


const Tools = () => {
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }, reload] = useFetch(getTools, [filter]);
  const { results: listData = [], count = 0 } = data || {};

  const [visible, setVisible] = useState(false);
  const [selectTool, setSelectTool] = useState<ToolData>(null);

  const onUpdatePermHandle = (tool: ToolData) => {
    setVisible(true);
    setSelectTool(tool);
  };

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultValue="tools" size="large">
            <TabPanel label={t('工具列表')} value="tools" />
          </Tabs>
        </Col>
        <Col flex="none" />
      </Row>
      <Search fields={TOOL_SEARCH_FIELDS} loading={false} searchParams={searchParams} />
      <ToolPermModal
        visible={visible}
        toolinfo={selectTool}
        onCancel={() => setVisible(false)}
        onOk={() => {
          reload();
          setVisible(false);
        }}
      />
      <div className="px-lg">
        <ToolTable
          onEdit={onUpdatePermHandle}
          dataSource={listData}
          loading={isLoading}
          pagination={{
            current: currentPage,
            total: count,
            pageSize,
          }}
        />
      </div>
    </>
  );
};

export default Tools;
