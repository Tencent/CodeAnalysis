import React, { useEffect, useState } from 'react';
import { t } from '@src/utils/i18n';
import { Tabs } from 'tdesign-react';

// 模块内
import { tagAPI } from '@src/services/nodes';

// 项目内
import NodeTable from '@plat/modules/nodes/node-table';
import TagTable from '@plat/modules/nodes/tag-table';
import s from './style.scss';

const { TabPanel } = Tabs;

const Nodes = () => {
  const [tags, setTags] = useState([]);
  const [tagOptions, setTagOptions] = useState([]);

  const getData = async () => {
    const res: any = await tagAPI.get({ limit: 1000 });
    const tags: any[] = res.results || [];
    setTags(tags);
    setTagOptions(tags.map(tag => ({
      label: tag.display_name || tag.name,
      value: tag.name,
    })));
  };

  useEffect(() => {
    getData();
  }, []);

  return (
    <>
      <Tabs defaultValue="nodes" size="large" className={s.header}>
        <TabPanel label={t('节点列表')} value="nodes">
          <NodeTable tagOptions={tagOptions} />
        </TabPanel>
        <TabPanel label={t('标签列表')} value="tags">
          <TagTable tags={tags} reload={() => {
            getData();
          }} />
        </TabPanel>
      </Tabs>
    </>
  );
};

export default Nodes;
