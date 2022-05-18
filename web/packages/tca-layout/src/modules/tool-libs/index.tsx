/**
 * 工具依赖
 */

import React, { useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import qs from 'qs';
import { omitBy, toNumber, omit, isString, cloneDeep, find } from 'lodash';
import { Table, Button } from 'coding-oa-uikit';
import EditIcon from 'coding-oa-uikit/lib/icon/Edit';

import { getQuery, formatDateTime } from '../../utils';
import { getToolLibs } from '@src/services/tools';
import { getTeamMember } from '@src/services/team';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useStateStore } from '@src/context/store';

import { LIB_TYPE } from './constants';
import CreateToollibs from './create-libs';
import Search from './search';
import style from './style.scss';

const Column = Table.Column;

export const ToolLibs = () => {
  const history = useHistory();
  const { orgSid }: any = useParams();
  const { userinfo } = useStateStore();
  const [admins, setAdmins] = useState([]);
  const [modalData, setModalData] = useState({
    visible: false,
    libId: null
  });
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const searchParams: any = omit(query, ['offset', 'limit']);
  const isAdmin = !!find(admins, { username: userinfo.username });  // 当前用户是否是管理员
  const isSuperuser = userinfo.is_superuser;  // 是否为超级管理员

  useEffect(() => {
    getTeamMember(orgSid).then((res) => {
      setAdmins(res.admins || []);
    });
  }, [orgSid]);

  useEffect(() => {
    getListData();
  }, []);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => isString(item) && !item),
    };

    setLoading(true);
    getToolLibs(orgSid, params)
      .then(response => {
        history.replace(`${location.pathname}?${qs.stringify(params)}`);
        setCount(response.count);
        setList(response.results);
      })
      .finally(() => {
        setLoading(false);
      })
  }

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  return (
    <div className={style.toollibs}>
      <div className={style.header}>
        <span className={style.title}>工具依赖</span>
      </div>
      <Search
        orgSid={orgSid}
        loading={loading}
        editable={isAdmin}
        searchParams={cloneDeep(searchParams)}
        onAdd={() => setModalData({
          visible: true,
          libId: null
        })}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
      />
      <Table
        loading={loading}
        dataSource={list}
        className={style.libsTable}
        pagination={{
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
          onChange: onChangePageSize
        }}
      >
        <Column
          title='依赖名称'
          dataIndex='name'
        />
        <Column
          title='环境变量'
          dataIndex='envs'
        // render={(envs: any) => envs && (
        //   // todo: 没有按顺序遍历出环境变量，环境变量是否有顺序依赖关系？
        //   Object.entries(envs).map(([key, value]) => (
        //     <p className={style.envs} key={key}>&quot;{key}&ldquo;:&quot;{value}&ldquo;</p>
        //   ))
        // )}
        />
        <Column
          title='依赖系统'
          dataIndex='lib_os'
        />
        <Column
          title='类型'
          dataIndex='lib_type'
          render={(lib_type: string) => LIB_TYPE[lib_type] || lib_type}
        />
        <Column
          title='创建时间'
          dataIndex='created_time'
          render={(time: any) => time && formatDateTime(time)}
        />
        <Column
          title='创建人'
          dataIndex={['creator', 'nickname']}
        />
        {
          isAdmin && (
            <Column
              title='操作'
              dataIndex='id'
              render={(id: number) => (
                <Button
                  type='text'
                  icon={<EditIcon />}
                  onClick={() => setModalData({
                    visible: true,
                    libId: id
                  })}
                />
              )}
            />
          )
        }
      </Table>
      {
        (isAdmin || isSuperuser) && (
          <CreateToollibs
            orgSid={orgSid}
            isSuperuser={isSuperuser}
            visible={modalData.visible}
            libId={modalData.libId}
            onClose={() => setModalData({
              visible: false,
              libId: null
            })}
            callback={() => getListData()}
          />
        )
      }
    </div>
  )
}

export default ToolLibs;