import React, { useState, useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import cn from 'classnames';
import { find, cloneDeep, get } from 'lodash';
import { Typography, Tooltip, Tag } from 'coding-oa-uikit';
import LogIcon from 'coding-oa-uikit/lib/icon/Log';
import GroupIcon from 'coding-oa-uikit/lib/icon/Group';
import ClockIcon from 'coding-oa-uikit/lib/icon/Clock';

import { useStateStore } from '@src/context/store';
import { formatDateTime, getQuery } from '@src/utils';
import { getToolsRouter } from '@src/utils/getRoutePath';
import { getTools } from '@src/services/tools';
import { getTeamMember } from '@src/services/team';
import { TOOL_STATUS, STATUSENUM } from './constants';
import CreateTool from './create-tool';
import Search from './search';

import style from './style.scss';

const DEFAULT_PAGER = {
  count: 0,
  pageStart: 0,
};

const DEFAULT_SIZE = 50;

const Tools = () => {
  const history = useHistory();
  const { userinfo } = useStateStore();
  const { orgSid }: any = useParams();
  const query = getQuery();
  const [visible, setVisible] = useState(false);
  const [admins, setAdmins] = useState([]);
  const [data, setData] = useState<any>([]);
  const [loading, setLoading] = useState(false);
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const { count, pageStart } = pager;
  const isAdmin = !!find(admins, { username: userinfo.username });  // 当前用户是否是管理员

  useEffect(() => {
    getData(DEFAULT_PAGER.pageStart, query);
    getTeamMember(orgSid).then((res) => {
      setAdmins(res.admins || []);
    });
  }, [orgSid]);

  const getData = (pageStart: number, params: any, isMore = false) => {
    setLoading(true);
    getTools(orgSid, {
      offset: pageStart,
      limit: DEFAULT_SIZE,
      ...params,
    }).then((res) => {
      const list = res.results || [];
      setData(isMore ? [...data, ...list] : list);
      setPager({
        count: res.count,
        pageStart,
      });
    })
      .finally(() => setLoading(false));
  };

  const onScroll = (e: any) => {
    // 滚动条触底加载更多数据
    if (e.target.scrollTop + e.target.clientHeight === e.target.scrollHeight) {
      if (data.length !== count) {
        getData(pageStart + DEFAULT_SIZE, query, true);
      }
    }
  };

  return (
    <div className={style.tools}>
      <div className={style.header}>
        <p className={style.title}>工具管理</p>
        <p className={style.desc}>共 {count} 个工具，包含公开工具 + 团队可用工具，团队成员可使用工具规则，仅团队管理员能添加工具和规则</p>
      </div>
      <Search
        orgSid={orgSid}
        loading={loading}
        searchParams={cloneDeep(query)}
        editable={isAdmin}
        onAdd={() => setVisible(true)}
        callback={(params: any) => {
          getData(DEFAULT_PAGER.pageStart, params);
        }}
      />
      <div
        className={style.contentWrapper}
        onScrollCapture={onScroll}
      >
        <div className={style.content}>
          {
            data.map((item: any) => (
              <div key={item.id} onClick={() => {
                history.push(`${getToolsRouter(orgSid)}/${item.id}/rules`);
              }}>
                <div className={style.toolHeader}>
                  <span className={style.title}>{item.display_name}</span>
                  {
                    item.status !== STATUSENUM.NORMAL && (
                      <Tag className={cn(style.tag, style[`status-${item.status}`])}>{get(TOOL_STATUS, item.status)}</Tag>
                    )
                  }
                  {
                    item.build_flag && (
                      <Tag className={cn(style.tag, style.build)}>需要编译</Tag>
                    )
                  }
                  {
                    item?.open_maintain && (
                      <Tooltip title='表示该工具可自定义规则'>
                        <Tag className={cn(style.tag, style.maintain)}>协同</Tag>
                      </Tooltip>
                    )
                  }
                  {
                    orgSid === item?.org_detail?.org_sid && (
                      <Tooltip title='由本团队创建的工具'>
                        <Tag className={cn(style.tag, style.custom)}>自定义</Tag>
                      </Tooltip>
                    )
                  }
                </div>
                <div className={style.detailWrapper}>
                  <LogIcon className={style.icon} />
                  <Tooltip title={item.description}>
                    <Typography.Paragraph className={style.descParagraph} ellipsis={{ rows: 1 }}>
                      {item.description}
                    </Typography.Paragraph>
                  </Tooltip>
                </div>
                <div className={style.detailWrapper}>
                  <GroupIcon className={style.icon} />
                  <span>{item?.org_detail?.name}</span>
                </div>
                <div className={style.detailWrapper}>
                  <ClockIcon className={style.icon} />
                  <span>{formatDateTime(item.created_time)}</span>
                </div>
              </div>
            ))
          }
        </div>
      </div>
      <CreateTool
        orgId={orgSid}
        visible={visible}
        onClose={() => setVisible(false)}
      />
    </div>
  );
};

export default Tools;
