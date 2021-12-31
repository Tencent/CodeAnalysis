/**
 * 分支概览代码检查详情
 */
import React, { useState } from 'react';
import { Radio, Row, Col } from 'coding-oa-uikit';
import get from 'lodash/get';

// 项目内
import NoData from '../no-data';
import Line from '@src/components/charts/line';
import DataCombinatePie from '@src/components/charts/data-combinate-pie';
import s from '../style.scss';
import { t } from '@src/i18n/i18next';
import { getLintPieChartData, getLintLineChartData } from '../utils';

export const LINT_TYPE = {
  SEVERITY: 'severity',
  CATEGORY: 'category',
  TABLE: 'table',
};

export const LINT_TYPE_TXT = {
  SEVERITY: t('问题级别'),
  CATEGORY: t('问题类型'),
  TABLE: t('详细数据'),
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
  TOTAL: t('总数'),
  UNDEAL: t('未处理'),
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

interface ITableProps {
  data: Array<any>;
}

const LintDetailTable = ({ data }: ITableProps) => (
  <table className={s.issueDetailTable}>
    <thead>
      <tr className={`${s.des} ${s.issueDetailTr}`}>
        <th>{t('问题分类')}</th>
        <th>{t('严重级别')}</th>
        <th>{t('状态')}</th>
        <th>{t('数量')}</th>
      </tr>
    </thead>
    <tbody className={s.detailTableBody}>
      {data.length === 0 ? (
        <tr className={s.issueDetailTr}>
          <td className={s.des} colSpan={4}>
            {t('没有数据')}
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
      <DataCombinatePie data={chanrtData} />
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
  const lintLineData = get(lineChartDatas, historyTypeValue, []);
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
              <Line
                data={lintLineData}
                xAxisKey="date"
                yAxisKey="num"
                cols={{
                  date: {
                    range: [0, 1],
                    tickCount: 5,
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
