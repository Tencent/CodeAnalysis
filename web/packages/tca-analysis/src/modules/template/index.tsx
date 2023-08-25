// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析模板入口文件
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { get } from 'lodash';
import { t } from '@src/utils/i18n';
import { Row, Col, Button, Loading } from 'tdesign-react';

import { useURLParams } from '@tencent/micro-frontend-shared/hooks';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';

import { getTmplList } from '@src/services/template';
import { getLanguages, getTags } from '@src/services/schemes';
import { TEMPLATE_FILTER_FIELDS as filterFields, TEMPLATE_SEARCH_FIELDS } from '@src/constant';

import TemplateCard from './tmpl-card';
import Create from './create';
import style from './style.scss';

const cardLayout = {
  xs: 6,
  sm: 6,
  md: 6,
  lg: 6,
  xl: 6,
  xxl: 4,
};

const DEFAULT_LOAD_SIZE = 60;

const Template = () => {
  const { orgSid } = useParams() as any;
  const [list, setList] = useState<any>([]);
  const [visible, setVisible] = useState(false);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [pager, setPager] = useState<any>({
    count: 0,
    pageStart: 0,
    pageSize: 12,
  });
  const { count, pageStart } = pager;
  const [languages, setLanguages] = useState<any>([]);

  const { searchParams } = useURLParams(filterFields);

  const getListData = useCallback((offset = 0, limit = DEFAULT_LOAD_SIZE, isMore = false) => {
    setLoading(true);
    const params = {
      offset,
      limit,
      ...searchParams,
    };
    getTmplList(orgSid, params).then((res: any) => {
      setPager({
        count: res.count,
        pageStart: offset + limit,
        pageSize: limit,
      });
      const listData = res.results || [];
      if (isMore) {
        setList((prevList: any[]) => [...prevList, ...listData]);
      } else {
        setList(listData);
      }
    })
      .finally(() => {
        setLoading(false);
        setLoadingMore(false);
      });
  }, [orgSid, searchParams]);

  useEffect(() => {
    getListData();
  }, [getListData]);

  useEffect(() => {
    (async () => {
      setTags(get(await getTags(orgSid), 'results', []));
      setLanguages(get(await getLanguages(), 'results', []));
    })();
  }, [orgSid]);

  const onScroll = (e: any) => {
    // 滚动条触底加载更多数据
    if (e.target.scrollTop + e.target.clientHeight === e.target.scrollHeight) {
      if (!loading && list.length < count) {
        setLoadingMore(true);
        getListData(pageStart, pageStart + DEFAULT_LOAD_SIZE, true);
      }
    }
  };

  return (
    <>
      <PageHeader title={t('分析方案模板')} description={t('分析方案模版用于在创建分析方案时作为模版参考。分析方案模版全局可用，不用和某个代码库关联。')} action={
        <Button theme="primary" onClick={() => setVisible(true)}>
          创建模板
        </Button>
      } />
      <Search
        fields={TEMPLATE_SEARCH_FIELDS}
        searchParams={searchParams}
      />
      <div
        className={style.contentWrapper}
        onScrollCapture={onScroll}
      >
        <Loading loading={loading && !loadingMore}>
          <div className={style.content}>
            <Row gutter={[16, 16]}>
              {list.map((data: any) => (
                <Col key={data.id} {...cardLayout}>
                  <TemplateCard
                    templateInfo={data}
                    languages={languages}
                  />
                </Col>
              ))}
            </Row>
            {loading && loadingMore && <div className={style.loading}><Loading size='small' loading={true} /></div>}
          </div>
        </Loading>
      </div>
      <Create
        orgSid={orgSid}
        visible={visible}
        tags={tags}
        languages={languages}
        onClose={() => setVisible(false)}
      />
    </>
  );
};

export default Template;
