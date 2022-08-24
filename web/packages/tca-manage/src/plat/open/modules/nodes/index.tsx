import React, { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Tabs } from 'tdesign-react';

// 模块内
import { tagAPI } from '@src/services/nodes';

// 项目内
import NodeTable from './node-table';
import TagTable from './tag-table';
import s from './style.scss';

const { TabPanel } = Tabs;

const Nodes = () => {
  const { t } = useTranslation();
  const [tags, setTags] = useState([]);
  const tagOptions = useMemo(() => tags.map((item: any) => ({
    label: item.display_name || item.name,
    value: item.name,
  })), [tags]);

  const getData = async () => {
    tagAPI.get({ limit: 1000 }).then((res: any) => {
      setTags(res.results || []);
    });
  };

  useEffect(() => {
    getData();
  }, []);

  return (
    <Tabs defaultValue="nodes" size="large" className={s.nodeHeader}>
      <TabPanel label={t('节点列表')} value="nodes" destroyOnHide={false}>
        <NodeTable tagOptions={tagOptions} />
      </TabPanel>
      <TabPanel label={t('标签列表')} value="tags" destroyOnHide={false}>
        <TagTable tags={tags} reload={() => {
          getData();
        }} />
      </TabPanel>
    </Tabs>
  );
};

export default Nodes;
