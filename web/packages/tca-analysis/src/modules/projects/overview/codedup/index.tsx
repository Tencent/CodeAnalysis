/**
 * 分支概览重复代码详情
 */
import React, { useState } from 'react';
import { Radio, Row, Col } from 'coding-oa-uikit';
import classnames from 'classnames';
import get from 'lodash/get';

// 项目内
import NoData from '../no-data';
import Line from '@src/components/charts/line';
import BarChart from '@src/components/charts/bar-chart';
import s from '../style.scss';
import { t } from '@src/i18n/i18next';
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
                            <BarChart
                                data={dupBarData}
                                xAxisKey="item"
                                yAxisKey="count"
                                cols={{
                                  count: { tickInterval: 5 },
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
                            <Line
                                data={dupLineData}
                                xAxisKey="date"
                                yAxisKey="num"
                                cols={{
                                  date: {
                                    range: [0, 1],
                                    tickCount: 5,
                                  },
                                }}
                                padding={[10, 'auto', 100, 'auto']}
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
