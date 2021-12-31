/**
 * 模板生成的分析方案列表
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Table } from 'coding-oa-uikit';
import { get } from 'lodash';

import { getSchemeRouter } from '@src/utils/getRoutePath';
import { DEFAULT_PAGER } from '@src/common/constants';
import { getSchemeList } from '@src/services/template';

import style from '../style.scss';

const { Column } = Table;

interface SchemeListProps {
  orgSid: string;
  teamName: string;
  tmplId: number;
}

const SchemeList = (props: SchemeListProps) => {
  const { orgSid, teamName, tmplId } = props;

  const [list, setList] = useState<any>([]);
  const [loading, setLoading] = useState(false);
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const { count, pageSize, pageStart } = pager;

  useEffect(() => {
    getListData();
  }, [tmplId]);

  const getListData = (offset = pageStart, limit = pageSize) => {
    setLoading(true);
    getSchemeList(orgSid, tmplId, { offset, limit }).then((response) => {
      setPager({
        pageSize: limit,
        pageStart: offset,
        count: response.count,
      });

      setList(response.results || []);
    })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  return (
        <Table
            dataSource={list}
            rowKey={(item: any) => item.id}
            loading={loading}
            className={style.schemeList}
            pagination={{
              size: 'default',
              current: Math.floor(pageStart / pageSize) + 1,
              total: count,
              pageSize,
              showSizeChanger: true,
              showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
              onChange: onChangePageSize,
              onShowSizeChange,
            }}
        >
            <Column
                title="分析方案名称"
                dataIndex="name"
                key="name"
                render={(name: string, data: any) => (
                    <Link className='link-name' target='_blank' to={`${getSchemeRouter(orgSid, teamName, get(data, 'repo.id'), data.id)}/basic`}>{name}</Link>
                )}
            />
            <Column
                title="所属代码库"
                dataIndex={['repo', 'scm_url']}
                key="repo"
            />
        </Table>
  );
};

export default SchemeList;
