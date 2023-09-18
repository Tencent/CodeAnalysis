/**
 * 仓库登记入口文件
 */
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button } from 'coding-oa-uikit';

import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';
import Search, { SearchFormField } from '@tencent/micro-frontend-shared/component/search';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';

import { getRepos } from '@src/services/common';
import { CLOSE_REPO_MEMBER_CONF } from '@plat/modules';
import List from './list';
import CreateRepoModal from './create-repo';
import style from './style.module.scss';

const filterFields: SearchFormField[] = [{
  name: 'scm_url_or_name',
  type: 'string',
  formType: 'input',
  placeholder: '别名/地址',
}];

const Repos = () => {
  const { orgSid, teamName }: any = useParams();
  const [visible, setVisible] = useState(false);

  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }, reload] = useFetch(getRepos, [orgSid, teamName, filter]);
  const { results: listData = [], count = 0 } = data || {};

  return (
    <div className={style.repos}>
      <PageHeader title='仓库登记' description='支持登记Git和SVN类型的代码库进行代码分析，Git代码库推荐使用OAUTH或专用的账号密码授权（从安全性考虑，不建议使用个人的账号密码）。'
        action={<Button type='primary' onClick={() => setVisible(true)}>代码库登记</Button>} />
      <Search loading={isLoading}
        fields={filterFields}
        searchParams={searchParams}
      />
      <div className={style.list}>
        <List
          orgSid={orgSid}
          teamName={teamName}
          searchWords={filter.scm_url_or_name as string}
          loading={isLoading}
          list={listData}
          callback={reload}
          pagination={{
            current: currentPage,
            total: count,
            pageSize,
          }}
          closeMemberConf={CLOSE_REPO_MEMBER_CONF}
        />
      </div>
      <CreateRepoModal
        orgSid={orgSid}
        teamName={teamName}
        visible={visible}
        onCancel={() => setVisible(false)}
        callback={() => reload()}
      />
    </div>
  );
};

export default Repos;
