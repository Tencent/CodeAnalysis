import React, { useState, useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import cn from 'classnames';
import { get } from 'lodash';
import { Typography, Tooltip, Tag, Button } from 'coding-oa-uikit';
import LogIcon from 'coding-oa-uikit/lib/icon/Log';
import GroupIcon from 'coding-oa-uikit/lib/icon/Group';
import ClockIcon from 'coding-oa-uikit/lib/icon/Clock';
import Search from '@tencent/micro-frontend-shared/component/search';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';
import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';
// 项目内
import { NAMESPACE, UserState } from '@src/store/user';
import { TOOL_STATUS_CHOICES, ToolStatusEnum, DEFAULT_PAGER } from '@src/constant';
import { getToolsRouter } from '@src/utils/getRoutePath';
import { getTools } from '@src/services/tools';
import { TOOL_FILTER_FIELDS as filterFields, TOOL_SEARCH_FIELDS } from './constants';
import CreateTool from './create-tool';
import style from './style.scss';

const DEFAULT_SIZE = 50;

const Tools = () => {
  const history = useHistory();
  const { t } = useTranslation();
  const { orgSid }: any = useParams();
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const isAdmin = useSelector((state: any) => state.APP)?.isOrgAdminUser ?? false;
  const isSuperuser = userinfo.is_superuser;  // 是否为超级管理员
  const editable = isAdmin || isSuperuser;  // 创建工具权限

  const [visible, setVisible] = useState(false);
  const [data, setData] = useState<any>([]);
  const [loading, setLoading] = useState(false);
  const [pager, setPager] = useState({ ...DEFAULT_PAGER, pageSize: DEFAULT_SIZE });
  const { count, pageSize, pageStart } = pager;
  const { searchParams } = useURLParams(filterFields);

  useEffect(() => {
    getData(DEFAULT_PAGER.pageStart, searchParams);
  }, [orgSid]);

  const getData = (pageStart: number, params: any, isMore = false) => {
    setLoading(true);
    getTools(orgSid, {
      offset: pageStart,
      limit: pageSize,
      ...params,
    }).then(({ results, count }: any) => {
      const list = results || [];
      setData(isMore ? [...data, ...list] : list);
      setPager({
        count,
        pageSize,
        pageStart,
      });
    })
      .finally(() => setLoading(false));
  };

  const onScroll = (e: any) => {
    // 滚动条触底加载更多数据
    if (e.target.scrollTop + e.target.clientHeight === e.target.scrollHeight) {
      if (data.length !== count) {
        getData(pageStart + DEFAULT_SIZE, searchParams, true);
      }
    }
  };

  return (
    <div className={style.tools}>
      <div className={style.header}>
        <p className={style.title}>{t('工具管理')}</p>
        <p className={style.desc}>{t(`共 ${count} 个工具，包含公开工具 + 团队可用工具，团队成员可使用工具规则，仅团队管理员能添加工具和规则`)}</p>
      </div>
      <Search style={{ paddingLeft: 30, paddingRight: 30 }} fields={TOOL_SEARCH_FIELDS} extraContent={
        editable && (
          <Button type='primary' onClick={() => {
            setVisible(true);
          }}>{t('创建工具')}</Button>
        )
      }
        loading={loading} searchParams={searchParams} callback={(params: any) => {
          getData(DEFAULT_PAGER.pageStart, params);
        }} />
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
                    item.status !== ToolStatusEnum.NORMAL && (
                      <Tag className={cn(style.tag, style[`status-${item.status}`])}>{get(TOOL_STATUS_CHOICES, item.status)}</Tag>
                    )
                  }
                  {
                    item.build_flag && (
                      <Tag className={cn(style.tag, style.build)}>{t('需要编译')}</Tag>
                    )
                  }
                  {
                    item.open_maintain && (
                      <Tooltip title={t('表示该工具可自定义规则')}>
                        <Tag className={cn(style.tag, style.maintain)}>{t('协同')}</Tag>
                      </Tooltip>
                    )
                  }
                  {
                    orgSid === item.org_detail?.org_sid && (
                      <Tooltip title={t('由本团队创建的工具')}>
                        <Tag className={cn(style.tag, style.custom)}>{t('自定义')}</Tag>
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
