// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支概览重复代码详情
 */
import React, { useState } from 'react';
import { Radio, Row, Col } from 'coding-oa-uikit';
import classnames from 'classnames';
import { t } from '@src/utils/i18n';
import get from 'lodash/get';

// 项目内
import NoData from '../no-data';
import { Area, Column } from '@ant-design/plots';

import s from '../style.scss';
import {
  STANDARD_TYPE,
  STANDARD_OPTIONS,
  RISK_TYPE,
  RISK_OPTIONS,
} from '@src/modules/projects/constants';
import { getDupLineChartData, getDupBarChartData } from '../utils';

interface IProps {
  dupScans: Array<any>;
}

const CodeDup = ({ dupScans }: IProps) => {
  const [standardValue, setStandardValue] = useState(STANDARD_TYPE.DEFAULT);
  const [riskValue, setRiskValue] = useState(RISK_TYPE.EXHI);
  // 获取重复代码历史趋势数据
  const lineChartDatas = getDupLineChartData(dupScans, standardValue);
  // 获取当前风险类型下的历史数据
  const dupLineData = get(lineChartDatas, riskValue, []);
  // 获取柱状图风险数据
  const dupBarData = getDupBarChartData(dupScans, standardValue);
  // 校验是否展示标准切换radio，如果最新的数据，不存在custom_summary，则不显示 radio
  const isShowStandardRadio = () => {
    let show = false;
    dupScans.forEach((item) => {
      if (!show && item.default_summary && item.custom_summary) {
        show = true;
      }
    });
    return show;
  };

  return (
    <div className={s.item}>
      <div className={classnames(s.header, 'overflow-hidden')}>
        <span className={s.tit}>{t('重复代码详情')}</span>
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
          <Col span={12}>{t('文件重复率分布')}</Col>
          <Col span={12}>{t('历史趋势')}</Col>
          <Col span={12} style={{ height: '222px' }}>
            {dupBarData.length > 0 ? (
              <Column
                data={dupBarData}
                xField="type"
                yField="value"
                maxColumnWidth={24}
                padding={[20, 30, 20, 40]}
                yAxis={{
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
              <NoData style={{ marginTop: '76px' }} />
            )}
          </Col>
          <Col span={12} className={s.borderLeft} style={{ height: '222px' }}>
            <Radio.Group
              value={riskValue}
              size="small"
              onChange={e => setRiskValue(e.target.value)}
            >
              {RISK_OPTIONS.map(item => (
                <Radio.Button key={item.value} value={item.value}>
                  {item.label}
                </Radio.Button>
              ))}
            </Radio.Group>
            {dupLineData.length > 0 ? (
              <Area
                data={dupLineData}
                xField="date"
                yField="num"
                padding={[20, 10, 50, 60]}
                yAxis={{
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

export default CodeDup;
