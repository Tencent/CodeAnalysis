import React from 'react';
import { Pie } from '@ant-design/plots';
import type { PieConfig } from '@ant-design/plots';
import { round } from 'lodash';

interface PieChartsProps {
  data: Record<string, any>[];
  confs?: Partial<PieConfig>
}

const PieCharts = ({ data, confs = {} }: PieChartsProps) => {
  const config: PieConfig = {
    data: data || [],
    angleField: 'value',
    colorField: 'type',
    radius: 0.6,
    innerRadius: 0.8,
    label: {
      type: 'outer',
      formatter(data) {
        return `${data.type}: ${data.value}（${round(data.percent * 100, 2)}%）`;
      },
    },
    legend: {
      layout: 'horizontal',
      position: 'bottom',
      offsetY: -20,
    },
    statistic: {
      title: false,
      content: false,
    },
    ...confs,
  };

  return (
    <Pie {...config} />
  );
};

export default PieCharts;
