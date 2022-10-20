/**
 * 仓库登记入口文件
 */
import React, { useState, useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import qs from 'qs';
import { toNumber, omit } from 'lodash';

// import { Button, Form, Input, Checkbox } from 'coding-oa-uikit';
import { Button, Form, Input } from 'coding-oa-uikit';
import Filter from '@src/components/filter';

import { getQuery } from '@src/utils';
import { getRepos } from '@src/services/common';
import { DEFAULT_PAGER } from '@src/constant';
import { CLOSE_REPO_MEMBER_CONF } from '@plat/modules';

import List from './list';
import CreateRepoModal from './create-repo';
import style from './style.module.scss';

const Repos = () => {
  const [form] = Form.useForm();
  const history = useHistory();
  const { orgSid, teamName }: any = useParams();
  const query = getQuery() as any;
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [visible, setVisible] = useState(false);

  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const searchParams: any = omit(query, ['offset', 'limit']);

  useEffect(() => {
    getListData();
  }, [orgSid, teamName]);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams) => {
    const params = {
      limit,
      offset,
      scope: 'related_me',  // 默认展示有权限的代码库
      ...otherParams,
    };
    setLoading(true);
    getRepos(orgSid, teamName, params).then((response) => {
      history.replace(`?${qs.stringify(params)}`);
      setCount(response.count);
      setList(response.results || []);
    })
      .finally(() => {
        setLoading(false);
        form.resetFields();
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onChangeSearchParams = (type: string, value: any) => {
    getListData(DEFAULT_PAGER.pageStart, pageSize, {
      ...searchParams,
      [type]: value,
    });
  };

  return (
    <div className={style.repos}>
      <header className={style.repoHeader}>
        <span>仓库登记</span>
        <div>
          <Button type='primary' onClick={() => setVisible(true)}>代码库登记</Button>
        </div>
      </header>
      <div className={style.search}>
        <Filter
          form={form}
          initialValues={{
            scm_url_or_name: query.scm_url_or_name,
            scope: query.scope === 'subscribed',
          }}
        >
          <Filter.Item label="" name="scm_url_or_name">
            <Input.Search
              size='middle'
              style={{ width: 200 }}
              placeholder="代码库别名/地址"
              allowClear
              onSearch={(value: string) => {
                onChangeSearchParams('scm_url_or_name', value);
              }}
            />
          </Filter.Item>
          {/* <Filter.Item
            label=""
            name="scope"
            valuePropName='checked'
          >
            <Checkbox
              onChange={(e: any) => {
                onChangeSearchParams('scope', e.target.checked ? 'subscribed' : 'related_me');
              }}
            >我关注的</Checkbox>
          </Filter.Item> */}
        </Filter>
      </div>
      <div className={style.list}>
        <List
          orgSid={orgSid}
          teamName={teamName}
          searchWords={query.scm_url_or_name}
          loading={loading}
          list={list}
          count={count}
          pageSize={pageSize}
          pageStart={pageStart}
          onChangePageSize={onChangePageSize}
          callback={getListData}
          closeMemberConf={CLOSE_REPO_MEMBER_CONF}
        />
      </div>
      <CreateRepoModal
        orgSid={orgSid}
        teamName={teamName}
        visible={visible}
        onCancel={() => setVisible(false)}
        callback={() => getListData(DEFAULT_PAGER.pageStart)}
      />
    </div>
  );
};

export default Repos;
