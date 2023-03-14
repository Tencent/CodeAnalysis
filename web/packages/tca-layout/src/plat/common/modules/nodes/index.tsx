import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { filter } from 'lodash';
import { Tabs } from 'coding-oa-uikit';

// 项目内
import { getTags } from '@src/services/nodes';

// 模块内
import NodeTable from './node-table';
import TagTable from './tag-table';

const { TabPane } = Tabs;

const Nodes = () => {
  const [tags, setTags] = useState([]);
  const { orgSid }: any = useParams();
  const tagOptions = useMemo(() => tags.map((item: any) => ({
    label: item.display_name || item.name,
    value: item.name,
  })), [tags]);

  const getData = async () => {
    getTags(orgSid, { limit: 1000 }).then((res: any) => {
      setTags(filter(res?.results, (item: any) => item?.org_sid === orgSid) || []);
    });
  };

  useEffect(() => {
    getData();
  }, []);

  return (
    <>
      <div className="px-lg">
        <Tabs defaultActiveKey="nodes" size="large">
          <TabPane tab={t('节点列表1')} key="nodes">
            <NodeTable tagOptions={tagOptions}/>
          </TabPane>
          <TabPane tab={t('标签列表')} key="tags">
            <TagTable tags={tags} reload={() => {
              getData();
            }} />
          </TabPane>
        </Tabs>
      </div>
    </>
  );
};

export default Nodes;
