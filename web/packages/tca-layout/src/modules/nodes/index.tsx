import React from 'react';
import { Tabs } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';

// 模块内
import NodeTable from './node-table';
import TagTable from './tag-table';

const { TabPane } = Tabs;

const Nodes = () => (
  <>
    <div className="px-lg">
      <Tabs defaultActiveKey="nodes" size="large">
        <TabPane tab={t('节点列表')} key="nodes">
          <NodeTable />
        </TabPane>
        <TabPane tab={t('标签列表')} key="tags">
          <TagTable />
        </TabPane>
      </Tabs>
    </div>
  </>
);

export default Nodes;
