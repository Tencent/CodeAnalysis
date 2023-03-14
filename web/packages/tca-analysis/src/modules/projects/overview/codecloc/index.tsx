// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支概览代码统计详情
 */
import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { Radio, Row, Col } from 'coding-oa-uikit';
import { get, minBy } from 'lodash';

// 项目内
import s from '../style.scss';
import { getClocLineChartData, getClocPieChartData } from '../utils';
import PieCharts from '@src/components/charts/pie';
import { Area } from '@ant-design/plots';
import NoData from '../no-data';

export const CLOC_TYPE = {
  TOTAL: 'total',
  CODE: 'code',
  COMMENT: 'comment',
  BLANK: 'blank',
};

export const CLOC_TYPE_TXT = {
  TOTAL: '总数',
  CODE: '代码',
  COMMENT: '注释',
  BLANK: '空白',
};

const CLOC_TYPE_OPTIONS = [
  { label: CLOC_TYPE_TXT.TOTAL, value: CLOC_TYPE.TOTAL },
  { label: CLOC_TYPE_TXT.CODE, value: CLOC_TYPE.CODE },
  { label: CLOC_TYPE_TXT.COMMENT, value: CLOC_TYPE.COMMENT },
  { label: CLOC_TYPE_TXT.BLANK, value: CLOC_TYPE.BLANK },
];

const colors: any = {
  代码: '#0066ff',
  注释: '#8cc6ff',
  空白: '#cceaff',
};

interface IProps {
  clocScans: Array<any>;
}

const CodeCloc = ({ clocScans }: IProps) => {
  const [typeValue, setTypeValue] = useState(CLOC_TYPE.TOTAL);
  const lineChartDatas = getClocLineChartData(clocScans);
  // 获取当前类型的line数据
  const clocLineData: Array<any> = get(lineChartDatas, typeValue, []);
  // 获取饼图数据
  const clocPieData = getClocPieChartData(clocScans);

  return (
    <div className={s.item}>
      <p className={s.header}>
        <span className={s.tit}>{t('代码统计详情')}</span>
      </p>
      <div className={s.content}>
        <Row gutter={[40, 14]}>
          <Col span={12}>{t('代码分布')}</Col>
          <Col span={12}>{t('代码量趋势')}</Col>
          <Col span={12} style={{ height: '222px' }}>
            {clocPieData.length > 0 ? (
              <PieCharts
                data={clocPieData}
                confs={{
                  color: ({ type }) => colors[type] || '#0066ff',
                }}
              />
            ) : (
              <NoData style={{ marginTop: '76px' }} />
            )}
          </Col>
          <Col span={12} className={s.borderLeft} style={{ height: '222px' }}>
            <Radio.Group
              value={typeValue}
              size="small"
              onChange={e => setTypeValue(e.target.value)}
            >
              {CLOC_TYPE_OPTIONS.map(item => (
                <Radio.Button key={item.value} value={item.value}>
                  {item.label}
                </Radio.Button>
              ))}
            </Radio.Group>
            {clocLineData.length > 0 ? (
              <Area
                data={clocLineData}
                xField="date"
                yField="num"
                padding={[20, 10, 50, 60]}
                yAxis={{
                  min: minBy(clocLineData, 'num')?.num - 1,
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

export default CodeCloc;
