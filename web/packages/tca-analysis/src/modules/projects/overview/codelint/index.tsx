// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支概览代码检查详情
 */
import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { Radio, Row, Col } from 'coding-oa-uikit';
import { get, minBy } from 'lodash';


// 项目内
import NoData from '../no-data';
import PieCharts from '@src/components/charts/pie';
import { Area } from '@ant-design/plots';

import s from '../style.scss';
import { getLintPieChartData, getLintLineChartData } from '../utils';

export const LINT_TYPE = {
  SEVERITY: 'severity',
  CATEGORY: 'category',
  TABLE: 'table',
};

export const LINT_TYPE_TXT = {
  SEVERITY: '问题级别',
  CATEGORY: '问题类型',
  TABLE: '详细数据',
};

const LINT_TYPE_OPTIONS = [
  {
    label: LINT_TYPE_TXT.SEVERITY,
    value: LINT_TYPE.SEVERITY,
  },
  {
    label: LINT_TYPE_TXT.CATEGORY,
    value: LINT_TYPE.CATEGORY,
  },
  {
    label: LINT_TYPE_TXT.TABLE,
    value: LINT_TYPE.TABLE,
  },
];

export const LINT_HISTORY_TYPE = {
  TOTAL: 'total',
  UNDEAL: 'undeal',
};

export const LINT_HISTORY_TYPE_TXT = {
  TOTAL: '总数',
  UNDEAL: '未处理',
};

const LINT_HISTORY_OPTIONS = [
  {
    label: LINT_HISTORY_TYPE_TXT.TOTAL,
    value: LINT_HISTORY_TYPE.TOTAL,
  },
  {
    label: LINT_HISTORY_TYPE_TXT.UNDEAL,
    value: LINT_HISTORY_TYPE.UNDEAL,
  },
];

const colors: any = {
  致命: '#eb333f',
  错误: '#f76469',
  警告: '#fba337',
  提示: '#ffe0b3',
  功能: '#0066ff',
  安全: '#3d98ff',
  代码风格: '#8cc6ff',
  其他: '#cceaff',
};

interface ITableProps {
  data: Array<any>;
}

const LintDetailTable = ({ data }: ITableProps) => (
  <table className={s.issueDetailTable}>
    <thead>
      <tr className={`${s.des} ${s.issueDetailTr}`}>
        <th>问题分类</th>
        <th>严重级别</th>
        <th>状态</th>
        <th>数量</th>
      </tr>
    </thead>
    <tbody className={s.detailTableBody}>
      {data.length === 0 ? (
        <tr className={s.issueDetailTr}>
          <td className={s.des} colSpan={4}>
            没有数据
          </td>
        </tr>
      ) : (
        <>
          {data.map((item: any, index: any) => (
            <tr key={index} className={`fs-12 ${s.issueDetailTr}`}>
              <td>{item.category}</td>
              <td>{item.severity}</td>
              <td>{item.state}</td>
              <td>{item.counts}</td>
            </tr>
          ))}
        </>
      )}
    </tbody>
  </table>
);

interface IChartProps {
  type: string;
  data: any;
}

const LintDetailChart = ({ type, data }: IChartProps) => {
  let node = null;
  let chanrtData = null;
  switch (type) {
    case LINT_TYPE.TABLE:
      node = <LintDetailTable data={data.rows} />;
      break;
    case LINT_TYPE.SEVERITY:
      chanrtData = data.severity;
      break;
    case LINT_TYPE.CATEGORY:
      chanrtData = data.category;
      break;
    default:
      node = <></>;
      break;
  }
  if (!node) {
    return chanrtData?.length > 0 ? (
      <PieCharts
      data={chanrtData}
      confs={{
        color: ({ type }: { type: string }) => colors[type] || '#0066ff',
      }}
    />
    ) : (
      <NoData style={{ marginTop: '52px' }} />
    );
  }
  return node;
};

interface IProps {
  lintScans: Array<any>;
}

const CodeLint = ({ lintScans }: IProps) => {
  const [undealTypeValue, setUndealTypeValue] = useState(LINT_TYPE.SEVERITY);
  const [totalTypeValue, setTotalTypeValue] = useState(LINT_TYPE.SEVERITY);
  const [historyTypeValue, setHistoryTypeValue] = useState(LINT_HISTORY_TYPE.TOTAL);
  const { undealData, totalData } = getLintPieChartData(lintScans);
  const lineChartDatas = getLintLineChartData(lintScans);
  const lintLineData: Array<any> = get(lineChartDatas, historyTypeValue, []);
  return (
    <div className={s.item}>
      <p className={s.header}>
        <span className={s.tit}>{t('代码检查')}</span>
      </p>
      <div className={s.content}>
        <Row gutter={[40, 14]}>
          <Col span={12}>{t('新增未处理问题分布')}</Col>
          <Col span={12}>{t('存量未处理问题分布')}</Col>
          <Col span={12} style={{ height: '250px' }}>
            <Radio.Group
              className=" mb-12"
              value={undealTypeValue}
              size="small"
              onChange={e => setUndealTypeValue(e.target.value)}
            >
              {LINT_TYPE_OPTIONS.map(item => (
                <Radio.Button key={item.value} value={item.value}>
                  {item.label}
                </Radio.Button>
              ))}
            </Radio.Group>
            <LintDetailChart type={undealTypeValue} data={undealData} />
          </Col>
          <Col span={12} className={s.borderLeft} style={{ height: '250px' }}>
            <Radio.Group
              className=" mb-12"
              value={totalTypeValue}
              size="small"
              onChange={e => setTotalTypeValue(e.target.value)}
            >
              {LINT_TYPE_OPTIONS.map(item => (
                <Radio.Button key={item.value} value={item.value}>
                  {item.label}
                </Radio.Button>
              ))}
            </Radio.Group>
            <LintDetailChart type={totalTypeValue} data={totalData} />
          </Col>
          <Col span={24}>{t('历史发现问题趋势')}</Col>
          <Col span={24} style={{ height: '240px' }}>
            <Radio.Group
              value={historyTypeValue}
              size="small"
              onChange={e => setHistoryTypeValue(e.target.value)}
            >
              {LINT_HISTORY_OPTIONS.map(item => (
                <Radio.Button key={item.value} value={item.value}>
                  {item.label}
                </Radio.Button>
              ))}
            </Radio.Group>
            {lintLineData.length > 0 ? (
              <Area
                data={lintLineData}
                xField="date"
                yField="num"
                padding={[20, 10, 50, 40]}
                yAxis={{
                  min: minBy(lintLineData, 'num')?.num - 1,
                  grid: {
                    line: {
                      style: {
                        stroke: '#e6e9ed',
                        lineDash: [3, 2],
                      },
                    },
                  },
                }}
              />
            ) : (
              <NoData style={{ marginTop: '52px' }} />
            )}
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default CodeLint;
