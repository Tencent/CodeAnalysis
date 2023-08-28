import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { Button } from 'tdesign-react';

import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import Search, { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';

import { getProjects } from '@src/services/team';
import List from './list';
import Modal from './modal';


const filterFields: SearchFormField[] = [{
  name: 'display_name',
  label: '项目名称',
  type: 'string',
  formType: 'input',
}, {
  name: 'scope',
  label: '项目类型',
  type: 'number',
  formType: 'select',
  options: [{
    label: '我管理的',
    value: 1,
  }],
}];


const Projects = () => {
  const { orgSid }: any = useParams();
  const history: any = useHistory();
  const [data, setData] = useState({
    loading: false,
    dataSource: [],
  });
  const [visible, setVisible] = useState(false);

  const getListData = useCallback((params = null) => {
    setData(pre => ({ ...pre, loading: true }));
    getProjects(orgSid, params).then((res: any[]) => {
      // 只显示未禁用的项目
      setData(({ loading: false, dataSource: res.filter(i => i.status === 1) }));
    })
      .finally(() => setData(pre => ({ ...pre, loading: false })));
  }, [orgSid]);

  useEffect(() => {
    getListData();
  }, [getListData]);

  useEffect(() => {
    // 用户从团队进入项目，如果不存在项目则默认弹出创建项目弹框
    if (history.location.state?.visible) {
      setVisible(true);
    }
  }, [history.location.state]);

  return (
    <>
      <PageHeader title="项目" description="一个团队可以具有多个项目，一个项目可以关联多个代码库" action={<Button theme='primary' onClick={() => setVisible(true)}>创建项目</Button>} />
      <Search fields={filterFields} searchParams={{}} route={false} callback={getListData} />
      <div className='tca-px-lg'>
        <List
          orgSid={orgSid}
          loading={data.loading}
          dataSource={data.dataSource}
        />
      </div>
      <Modal
        orgSid={orgSid}
        visible={visible}
        onClose={() => setVisible(false)}
        callback={() => getListData()}
      />
    </>
  );
};

export default Projects;
