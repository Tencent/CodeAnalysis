import React, { useEffect, useState } from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';
import { t } from '@src/utils/i18n';

// 模块内
import PageHeader, { PageHeaderTabProps } from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { tagAPI } from '@src/services/nodes';

// 项目内
import NodeTable from '@plat/modules/nodes/node-table';
import TagTable from '@plat/modules/nodes/tag-table';

const pageHeaderTab: PageHeaderTabProps = {
  options: [{
    label: t('节点管理'),
    value: 'nodes',
  }, {
    label: t('标签管理'),
    value: 'labels',
  }],
  routeChangeHandler: value => `/manage/nodemgr/${value}`,
};

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
      <PageHeader title="节点管理" tab={pageHeaderTab} />
      <Switch>
        <Route path='/manage/nodemgr/nodes' render={() => <NodeTable tagOptions={tagOptions} />} />
        <Route path='/manage/nodemgr/labels' render={() => <TagTable tags={tags} reload={() => {
          getData();
        }} />} />
        <Redirect from='/manage/nodemgr' to='/manage/nodemgr/nodes' />
      </Switch>
    </>
  );
};

export default Nodes;
