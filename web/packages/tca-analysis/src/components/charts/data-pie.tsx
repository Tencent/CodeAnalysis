// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      饼图组件
 */

import React from 'react';
import { Chart, Geom, Axis, Tooltip, Coord, Label, Legend } from 'bizcharts';
import DataSet from '@antv/data-set';

interface DataPieProps {
  data: Array<any>
}

const DataPie = (props: DataPieProps) => {
  const dv = new DataSet.DataView();
  dv.source(props.data).transform({
    type: 'percent',
    field: 'count',
    dimension: 'item',
    as: 'percent',
  });
  const cols = {
    percent: {
      formatter: (val) => {
        // eslint-disable-next-line no-param-reassign
        val = `${(val * 100).toFixed(2)}%`;
        return val;
      },
    },
  };
  return (
    <div>
      <Chart height={250} data={dv} scale={cols} padding={[10, 80, 80, 70]} forceFit>
        <Coord type="theta" radius={0.75} innerRadius={0.8} />
        <Axis name="percent" />
        <Legend position="bottom" />
        <Tooltip
          showTitle={false}
          itemTpl='<li><span style="background-color:{color};" class="g2-tooltip-marker"></span>{name}: {value}</li>'
        />
        <Geom
          type="intervalStack"
          position="percent"
          color={['item', ['#3655b3', '#5870fe', '#9ab3ff', '#c0d1ff']]}
          tooltip={[
            'item*percent',
            (item, percent) => {
              // eslint-disable-next-line no-param-reassign
              percent = `${(percent * 100).toFixed(2)}%`;
              return {
                name: item,
                value: percent,
              };
            },
          ]}
          style={{
            lineWidth: 1,
            stroke: '#fff',
          }}
        >
          <Label
            content="percent"
            formatter={(val, item) => `${item.point.item}: ${item.point.count}个(${val})`
            }
          />
        </Geom>
      </Chart>
    </div>
  );
};

export default DataPie;
