// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支概览圈复杂度详情
 */
import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { Radio, Row, Col } from 'coding-oa-uikit';
import classnames from 'classnames';
import { get, minBy } from 'lodash';

// 项目内
import NoData from '../no-data';
import PieCharts from '@src/components/charts/pie';
import { Area } from '@ant-design/plots';
import s from '../style.scss';
import { STANDARD_TYPE, STANDARD_OPTIONS } from '@src/modules/projects/constants';
import { getCyCLineChartData, getCycPieChartData } from '../utils';

export const CYC_TYPE = {
  TOTAL: 'total',
  OVER: 'over',
  EXCESS: 'excess',
};

export const CYC_TYPE_TXT = {
  TOTAL: '总数',
  OVER: '超标数',
  EXCESS: '未超标数',
};

const CYC_TYPE_OPTIONS = [
  {
    label: CYC_TYPE_TXT.TOTAL,
    value: CYC_TYPE.TOTAL,
  },
  {
    label: CYC_TYPE_TXT.OVER,
    value: CYC_TYPE.OVER,
  },
];

const colors: any = {
  超标数: '#eb333f',
  未超标数: '#0066ff',
};

interface IProps {
  cycScans: Array<any>;
}

const CodeCC = ({ cycScans }: IProps) => {
  const [typeValue, setTypeValue] = useState(CYC_TYPE.TOTAL);
  const [standardValue, setStandardValue] = useState(STANDARD_TYPE.DEFAULT);
  const cycLineDatas = getCyCLineChartData(cycScans, standardValue);
  const cycLineData = get(cycLineDatas, typeValue, []);
  const cycPieData = getCycPieChartData(cycScans, standardValue);

  // 校验是否展示标准切换radio，如果最新的数据，不存在custom_summary，则不显示 radio
  const isShowStandardRadio = () => {
    let show = false;
    cycScans.forEach((item) => {
      if (!show && item.default_summary && item.custom_summary) {
        show = true;
      }
    });
    return show;
  };

  return (
    <div className={s.item}>
      <div className={classnames(s.header, 'overflow-hidden')}>
        <span className={s.tit}>{t('圈复杂度详情')}</span>
        {isShowStandardRadio() && (
          <Radio.Group
            className="float-right"
            value={standardValue}
            size="small"
            onChange={e => setStandardValue(e.target.value)}
          >
            {STANDARD_OPTIONS.map(item => (
              <Radio.Button key={item.value} value={item.value}>
                {item.label}
              </Radio.Button>
            ))}
          </Radio.Group>
        )}
      </div>
      <div className={s.content}>
        <Row gutter={[40, 14]}>
          <Col span={12}>{t('方法圈复杂度分布')}</Col>
          <Col span={12}>{t('历史趋势')}</Col>
          <Col span={12} style={{ height: '222px' }}>
            {cycPieData.length > 0 ? (
              <PieCharts
                data={cycPieData}
                confs={{
                  color: ({ type }: { type: string }) => colors[type] || '#0066ff',
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
              {CYC_TYPE_OPTIONS.map(item => (
                <Radio.Button key={item.value} value={item.value}>
                  {item.label}
                </Radio.Button>
              ))}
            </Radio.Group>
            {cycLineData.length > 0 ? (
              <Area
                data={cycLineData}
                xField="date"
                yField="num"
                padding={[20, 10, 50, 60]}
                yAxis={{
                  min: minBy(cycLineData, 'num')?.num - 1,
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
        {/* <div className={`${s.panelContent}`} style={{ marginTop: '14px' }}>
                    <div className={s.chartBox}>
                        <p>{t('超标圈复杂度总数趋势')}</p>
                        <div className={s.chartCell}></div>
                    </div>
                    <div className={s.chartBox}>
                        <p>{t('千行代码平均圈复杂度')}</p>
                        <div className={`${s.chartCell} ${s.borderLeft}`}></div>
                    </div>
                </div> */}
      </div>
    </div>
  );
};

export default CodeCC;
